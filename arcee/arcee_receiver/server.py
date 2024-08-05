import time
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone, timedelta
import asyncio

from etcd import Lock as EtcdLock, Client as EtcdClient
from typing import Tuple
import os
import uuid

from mongodb_migrations.cli import MigrationManager
from mongodb_migrations.config import Configuration
from pydantic import ValidationError
from sanic import Sanic
from sanic.log import logger
from sanic.response import json
from sanic.exceptions import SanicException
import motor.motor_asyncio
from sanic_ext import validate

from arcee.arcee_receiver.models import (
    TaskPatchIn, Console, ConsolePostIn, Dataset, DatasetPatchIn,
    DatasetPostIn, Run, RunPatchIn, RunPostIn, LeaderboardDataset,
    LeaderboardDatasetPatchIn, LeaderboardDatasetPostIn,
    Leaderboard, LeaderboardPostIn, LeaderboardPatchIn, Log, Platform,
    StatsPostIn, ModelPatchIn, ModelPostIn, Model, ModelVersionIn,
    ModelVersion, Metric, MetricPostIn, MetricPatchIn,
    ArtifactPostIn, ArtifactPatchIn, Artifact, ArtifactSearchParams,
)
from arcee.arcee_receiver.modules.leader_board import (
    get_calculated_leaderboard, Tendencies)
from arcee.arcee_receiver.modules.leader_board import (
    get_metrics as _get_task_metrics)

from optscale_client.aconfig_cl.aconfig_cl import AConfigCl

app = Sanic("arcee")

etcd_host = os.environ.get('HX_ETCD_HOST')
etcd_port = int(os.environ.get('HX_ETCD_PORT', 0))
config_client = AConfigCl(host=etcd_host, port=etcd_port)

CHUNK_SIZE = 200
DAY_IN_SEC = 86400


@app.on_request
async def add_start_time(request):
    request.ctx.start_time = time.time()


@app.on_response
async def add_spent_time(request, response):
    spend_time = round((time.time() - request.ctx.start_time) * 1000)
    logger.info("{} {} {} {} {}ms".format(response.status, request.method,
                                          request.path, request.query_string,
                                          spend_time))


def get_arcee_db_params() -> Tuple[str, str, str, str, str]:
    arcee_db_params = config_client.arcee_params()
    return asyncio.run(arcee_db_params)


async def get_cluster_secret() -> str:
    return await config_client.cluster_secret()


name, password, host, port, db_name = get_arcee_db_params()
uri = "mongodb://{u}:{p}@{host}:{port}/admin".format(
    u=name, p=password, host=host, port=port)
client = motor.motor_asyncio.AsyncIOMotorClient(uri)
# https://stackoverflow.com/a/69065287
client.get_io_loop = asyncio.get_running_loop
db = client[db_name]


async def extract_token(request, raise_on=True):
    token = request.headers.get('x-api-key')
    if not token and raise_on:
        raise SanicException("API key is required", status_code=401)
    return token


async def check_token(token, raise_on=True):
    token = await db.token.find_one({
        "$and": [
            {"deleted_at": 0},
            {"token": token},
        ]
    })
    if not token and raise_on:
        raise SanicException("Token not found", status_code=401)
    return bool(token)


async def extract_secret(request, raise_on=True):
    secret = request.headers.get('Secret')
    if not secret and raise_on:
        raise SanicException("secret is required", status_code=401)
    return secret


async def check_secret(secret, raise_on=True):
    required = await get_cluster_secret()
    if raise_on:
        if secret != required:
            raise SanicException("secret is invalid", status_code=401)
    return secret == required


AUTH_VALIDATION_TYPES = ['secret', 'token', 'secret_or_token']


@app.on_request
async def handle_auth(request):
    # different validations according to route context

    if not request.route:
        # request.route is None on unknown URLs, sanic will raise 404
        return

    # having one of supported labels is a mandatory for arcee requests
    if (not hasattr(request.route.ctx, 'label')
            or request.route.ctx.label not in AUTH_VALIDATION_TYPES):
        raise SanicException('Unknown auth validation type', status_code=500)
    elif request.route.ctx.label == 'token':
        token = await extract_token(request)
        await check_token(token, raise_on=True)
        request.ctx.token = token
    elif request.route.ctx.label == 'secret':
        secret = await extract_secret(request, raise_on=True)
        await check_secret(secret, raise_on=True)
    elif request.route.ctx.label == 'secret_or_token':
        secret = await extract_secret(request, raise_on=False)
        is_valid_secret = await check_secret(secret, raise_on=False)
        if not is_valid_secret:
            token = await extract_token(request)
            await check_token(token, raise_on=True)
            request.ctx.token = token


async def check_run_state(run):
    # state is finished or error
    if run['state'] in [2, 3]:
        raise SanicException("Run is completed", status_code=409)


async def check_task(token, o):
    # check task
    p = await db.task.find_one({
        "_id": o["task_id"],
        "token": token,
        "deleted_at": 0
    })
    if not p:
        raise SanicException("given run not correspond to user",
                             status_code=403)


async def check_func(func):
    allowed = ("avg", "max", "sum", "last")
    if func not in allowed:
        msg = "invalid function, allowed: %s" % ','.join(allowed)
        raise SanicException(msg, status_code=400)


async def to_bool(val):
    val = val.lower()
    if val not in ['true', 'false']:
        raise SanicException(
            'invalid param, should be false or true', status_code=400)
    return val == 'true'


async def check_metrics(metrics):
    """
    Checks metrics
    :param metrics:
    :return:
    """
    if not isinstance(metrics, list):
        raise SanicException("metrics should be list", status_code=400)
    if not metrics:
        return
    existing_metrics = [
        doc["_id"] async for doc in db.metric.find({"_id": {"$in": metrics}})
    ]
    missing = list(filter(lambda x: x not in existing_metrics, metrics))
    if missing:
        msg = "some metrics not exists in db: %s" % ",".join(missing)
        raise SanicException(msg, status_code=400)


async def check_leaderboard_filters(leaderboard, updates):
    filters = updates.get('filters') or leaderboard.get('filters', {})
    primary_metric = updates.get('primary_metric') or leaderboard.get(
        'primary_metric')
    other_metrics = updates.get('other_metrics') or leaderboard.get(
        'other_metrics', [])
    metrics_ids = other_metrics + [primary_metric]
    filter_ids = [x['id'] for x in filters]
    if any(x not in metrics_ids for x in filter_ids):
        raise SanicException('Invalid filters', status_code=400)


@app.route('/arcee/v2/tasks', methods=["POST", ], ctx_label='token')
async def create_task(request):
    token = request.ctx.token
    doc = request.json
    # TODO: validators
    key = doc.get("key")
    if not key or not isinstance(key, str):
        raise SanicException("Key should be str", status_code=400)
    metrics = (doc.get("metrics") or list())
    await check_metrics(metrics)
    display_name = doc.get("name", key)
    description = doc.get("description")
    doc.update({"token": token})
    o = await db.task.find_one(
        {"token": token, "key": key, "deleted_at": 0})
    if o:
        raise SanicException("Project exists", status_code=409)
    doc["_id"] = str(uuid.uuid4())
    doc["name"] = display_name
    doc["deleted_at"] = 0
    doc["description"] = description
    await db.task.insert_one(doc)
    return json(doc)


@app.route('/arcee/v2/tasks/<id_>', methods=["PATCH", ],
           ctx_label='token')
@validate(json=TaskPatchIn)
async def update_task(request, body: TaskPatchIn, id_: str):
    """
    update task
    :param request:
    :param body:
    :param id_:
    :return:
    """
    token = request.ctx.token
    o = await db.task.find_one(
        {"token": token, "_id": id_, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    d = body.model_dump(exclude_unset=True)
    if d:
        metrics = d.get('metrics')
        if metrics is not None:
            await check_metrics(metrics)
            metrics_to_remove = set(o['metrics']) - set(metrics)
            for metric_id in metrics_to_remove:
                if await _metric_used_in_lb(db, metric_id, task_id=id_):
                    raise SanicException(
                        f"Metric is used in task leaderboard(s)",
                        status_code=409)
        await db.task.update_one(
            {"_id": id_}, {'$set': d})
    return json({"updated": bool(d), "id": id_})


@app.route('/arcee/v2/tasks', methods=["GET", ], ctx_label='token')
async def get_tasks(request):
    """
    Gets tasks names based on provided token
    :param request:
    :return:
    """
    token = request.ctx.token
    pipeline = [
        {"$match": {"token": token, "deleted_at": 0}},
        {
            "$lookup": {
                "from": "metric",
                "localField": "metrics",
                "foreignField": "_id",
                "as": "taskMetrics"
            }
        },
    ]
    cur = db.task.aggregate(pipeline)
    return json([i async for i in cur])


@app.route('/arcee/v2/tasks/bulk', methods=["GET", ], ctx_label='token')
async def bulk_get_tasks(request):
    """
    Bulk get tasks by task ids
    """
    token = request.ctx.token
    task_ids = request.args.getlist("task_id")
    if not task_ids:
        raise SanicException("task_id is required", status_code=400)
    match_filter = {
        "token": token,
        "_id": {"$in": task_ids},
        "deleted_at": 0
    }
    include_deleted = "include_deleted"
    if (include_deleted in request.args.keys() and
            await to_bool(request.args.get(include_deleted))):
        match_filter.pop('deleted_at')
    pipeline = [
        {"$match": match_filter},
        {
            "$lookup": {
                "from": "metric",
                "localField": "metrics",
                "foreignField": "_id",
                "as": "taskMetrics"
            }
        },
    ]
    cur = db.task.aggregate(pipeline)
    return json([i async for i in cur])


@app.route('/arcee/v2/tasks/<id_>', methods=["GET", ],
           ctx_label='token')
async def get_task(request, id_: str):
    """
    Gets tasks names based on provided task id
    :param request:
    :param id_:
    :return:
    """
    token = request.ctx.token
    o = await db.task.find_one(
        {"token": token, "_id": id_, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    pipeline = [
        {"$match": {"token": token, "_id": id_}},
        {
            "$lookup": {
                "from": "metric",
                "localField": "metrics",
                "foreignField": "_id",
                "as": "taskMetrics"
            }
        },
    ]
    cur = db.task.aggregate(pipeline)
    return json(await cur.next())


@app.route('/arcee/v2/tasks/<id_>', methods=["DELETE", ],
           ctx_label='token')
async def delete_task(request, id_: str):
    """
    Deletes tasks names based on provided task id
    :param request:
    :param id_:
    :return:
    """
    deleted_logs = 0
    deleted_milestones = 0
    deleted_runs = 0
    deleted_stages = 0
    deleted_proc_data = 0
    deleted_consoles = 0
    deleted_artifacts = 0
    token = request.ctx.token
    o = await db.task.find_one(
        {"token": token, "_id": id_, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    runs = [doc["_id"] async for doc in db.run.find({"task_id": id_})]
    if runs:
        results = await asyncio.gather(
            db.milestone.delete_many({'run_id': {'$in': runs}}),
            db.stage.delete_many({'run_id': {'$in': runs}}),
            db.proc_data.delete_many({'run_id': {'$in': runs}}),
            db.log.delete_many({'run_id': {'$in': runs}}),
            db.run.delete_many({"task_id": id_}),
            db.console.delete_many({'run_id': {'$in': runs}}),
            db.artifact.delete_many({'run_id': {'$in': runs}}),
        )
        dm, ds, dpd, dl, dr, dc, da = results
        deleted_milestones = dm.deleted_count
        deleted_stages = ds.deleted_count
        deleted_logs = dl.deleted_count
        deleted_runs = dr.deleted_count
        deleted_proc_data = dpd.deleted_count
        deleted_consoles = dc.deleted_count
        deleted_artifacts = da.deleted_count
    leaderboard = await db.leaderboard.find_one(
        {"token": token, "task_id": id_, "deleted_at": 0})
    now = int(datetime.now(tz=timezone.utc).timestamp())
    if leaderboard:
        datasets = [doc async for doc in db.leaderboard_dataset.find(
            {'leaderboard_id': leaderboard['_id'], 'deleted_at': 0},
            {'_id': 1})]
        await db.leaderboard_dataset.update_many(
            {"_id": {'$in': [x['_id'] for x in datasets]},
             'deleted_at': 0},
            {'$set': {"deleted_at": now}})
        await db.leaderboard.update_one(
            {"_id": leaderboard['_id']},
            {'$set': {"deleted_at": now}})
    await db.model_version.update_many(
        {"run_id": {'$in': runs}, 'deleted_at': 0},
        {"$set": {"deleted_at": now}})
    await db.task.update_one(
        {"_id": id_}, {"$set": {"deleted_at": now}})
    return json({
        "deleted": True,
        "_id": id_,
        "deleted_milestones": deleted_milestones,
        "deleted_logs": deleted_logs,
        "deleted_runs": deleted_runs,
        "deleted_stages": deleted_stages,
        "deleted_proc_data": deleted_proc_data,
        "deleted_console_output": deleted_consoles,
        "deleted_artifacts": deleted_artifacts
    })


@app.route('/arcee/v2/tasks/<name>/run', methods=["POST", ],
           ctx_label='token')
@validate(json=RunPostIn)
async def create_task_run(request, body: RunPostIn, name: str):
    """
    create task run
    :param body:
    :param request:
    :param name: str
    :return:
    """
    token = request.ctx.token

    o = await db.task.find_one(
        {"token": token, "key": name, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)

    task_id = o["_id"]
    run_cnt = await db.run.count_documents({"task_id": task_id})
    r = Run(
        task_id=task_id, number=run_cnt + 1, **body.model_dump()
    )

    await db.run.insert_one(r.model_dump(by_alias=True))
    return json({"id": r.id})


async def reached_goals(run):
    result = dict()
    func_map = {
        'more': lambda x, y: x >= y,
        'less': lambda x, y: x <= y,
    }

    task_metrics = run.get("task", {}).get("metrics", [])
    data_metrics = run.get("data", {})

    task_metrics_all = [
        doc async for doc in db.metric.find({"_id": {"$in": task_metrics}})
    ]

    metrics = {}
    for g in task_metrics:
        filtered_metrics = list(filter(
            lambda x: g == x["_id"], task_metrics_all))
        if filtered_metrics:
            gl = filtered_metrics[0]
            metrics[gl["key"]] = {
                "id": gl["_id"],
                "tendency": gl["tendency"],
                "target_value": gl["target_value"],
                "name": gl["name"],
            }

    for k, v in metrics.items():
        # add task metric
        result[k] = dict()
        result[k].update(v)
        g = data_metrics.get(k)
        if g is not None:
            func = func_map.get(v.get("tendency"), lambda x, y: False)
            reached = func(g, v["target_value"])
            result[k]["value"] = g
            result[k]["reached"] = reached
        else:
            result[k]["reached"] = False
    return result


@app.route('/arcee/v2/run/<run_id>', methods=["GET", ],
           ctx_label='secret_or_token')
async def get_run(request, run_id):
    """
    Gets task run by id
    :param request:
    :param run_id:
    :return:
    """
    token = getattr(request.ctx, 'token', None)
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    if token:
        # check project
        await check_task(token, o)
    pipeline = [
        {"$match": {"_id": run_id}},
        {
            "$lookup": {
                "from": "platform",
                "localField": "executors",
                "foreignField": "instance_id",
                "as": "runExecutors"
            }
        },
        {
            "$lookup": {
                "from": "task",
                "localField": "task_id",
                "foreignField": "_id",
                "as": "task"
            }
        },
        {
            "$unwind": '$task'
        }
    ]
    cur = db.run.aggregate(pipeline)
    run = await cur.next()
    reached = await reached_goals(run)
    run["reached_goals"] = reached
    return json(run)


@app.route('/arcee/v2/run/executors', methods=["GET", ], ctx_label='token')
async def get_executors(request):
    """
    Gets executors
    """
    token = request.ctx.token
    run_id = "run_id"
    task_id = "task_id"
    args = request.args
    supported_keys = [run_id, task_id]
    if len(args) != 1:
        raise SanicException("run_id / task_id is required",
                             status_code=400)
    if not any(filter(lambda x: x in supported_keys, request.args.keys())):
        raise SanicException("run_id / task_id is supported",
                             status_code=400)
    not_supported = list((filter(
        lambda x: x not in supported_keys, request.args.keys())))
    if not_supported:
        raise SanicException(
            "%s keys is not supported" % ','.join(not_supported),
            status_code=400)
    task_ids = []
    run_ids = []
    if task_id in request.args.keys():
        task_ids = request.args[task_id]
    if run_id in request.args.keys():
        run_ids = request.args[run_id]
    # ensure task ids provided for required token
    task_ids = [doc["_id"] async for doc in db.task.find(
        {
            "$and": [
                {"_id": {"$in": task_ids}},
                {"token": token},
                {"deleted_at": 0}
            ]}
    )]
    runs = [doc["_id"] async for doc in db.run.find(
        {
            "$or": [
                {"task_id": {"$in": task_ids}},
                {"_id": {"$in": run_ids}}
            ]}
    )]
    pipeline = [
        {"$match": {"_id": {"$in": runs}}},
        {"$unwind": "$executors"},
        {
            "$lookup": {
                "from": "platform",
                "localField": "executors",
                "foreignField": "instance_id",
                "as": "r"
            }
        },
        {
            "$replaceRoot": {
                "newRoot": {
                    "$mergeObjects": [
                        "$r"
                    ]
                }
            }
        },
        {
            "$group": {"_id": "$instance_id"}
        },
        {
            "$lookup": {
                "from": "platform",
                "localField": "_id",
                "foreignField": "instance_id",
                "as": "r"
            }
        },
        {
            "$replaceRoot": {
                "newRoot": {
                    "$mergeObjects": [
                        "$r"
                    ]
                }
            }
        },
    ]
    cur = db.run.aggregate(pipeline)
    return json([i async for i in cur])


@app.route('/arcee/v2/run/<run_id>', methods=["PATCH", ],
           ctx_label='secret_or_token')
@validate(json=RunPatchIn)
async def update_run(request, body: RunPatchIn, run_id: str):
    """
    update task run
    :param body:
    :param request:
    :param run_id: str
    :return:
    """
    # firstly we try to use token (used for bulldozer)
    token = getattr(request.ctx, 'token', None)

    r = await db.run.find_one({"_id": run_id})
    if not r:
        raise SanicException("Run not found", status_code=404)
    if token is not None:
        # omit check if accessed by secret
        await check_run_state(r)
        # check task
        await check_task(token, r)

    d = body.model_dump(exclude_unset=True, exclude={'finish'})
    # TODO: remove "finish" from PATCH payload. Set ts based on "state"
    if body.finish:
        d.update({"finish": int(datetime.utcnow().timestamp())})
    hyperparameters = d.get("hyperparameters", {})
    if hyperparameters:
        existing_hyperparams = r.get("hyperparameters", {})
        existing_hyperparams.update(hyperparameters)
        d.update({"hyperparameters": existing_hyperparams})

    await db.run.update_one(
        {"_id": run_id}, {'$set': d})
    return json({"updated": True, "id": run_id})


@app.route('/arcee/v2/run/<run_id>/milestones', methods=["POST", ],
           ctx_label='token')
async def create_run_milestone(request, run_id: str):
    """
    create project run milestone
    :param request:
    :param run_id: str
    :return:
    """
    token = request.ctx.token
    doc = request.json
    milestone = doc.get("milestone")
    # TODO: validators
    # find project with given name-token
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_run_state(o)
    await check_task(token, o)
    run_id = o["_id"]
    d = {
        "_id": str(uuid.uuid4()),
        "run_id": run_id,
        "timestamp": int(datetime.utcnow().timestamp()),
        "milestone": milestone,
    }
    await db.milestone.insert_one(
        d
    )
    return json({"id": d["_id"]})


@app.route('/arcee/v2/run/<run_id>/milestones', methods=["GET", ],
           ctx_label='token')
async def get_milestones(request, run_id: str):
    """
    Get milestones for run
    :param request:
    :param run_id:
    :return:
    """
    token = request.ctx.token
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_task(token, o)
    res = [doc async for doc in db.milestone.find({"run_id": run_id})]
    return json(res)


@app.route('/arcee/v2/collect', methods=["POST", ], ctx_label='token')
@validate(json=StatsPostIn)
async def collect(request, body: StatsPostIn):
    token = request.ctx.token

    platform = body.platform
    instance_id = platform.instance_id
    if instance_id:
        o = await db.platform.find_one({"instance_id": instance_id})
        if not o:
            await db.platform.insert_one(
                Platform(**platform.model_dump()).model_dump(by_alias=True))

    run_id = body.run
    run = await db.run.find_one({"_id": run_id})
    if not run:
        raise SanicException("Not found", status_code=404)
    await check_run_state(run)

    log = Log(instance_id=instance_id, project=body.project,
              run_id=body.run, data=body.data)
    await db.log.insert_one(log.model_dump(by_alias=True))

    executors = run.get("executors", [])
    if instance_id:
        executors.append(instance_id)
    old_data = run.get("data", {})
    new_data = body.data
    await db.run.update_one(
        {"_id": run_id}, {
            '$set': {
                "data": {**old_data, **new_data},
                "executors": list(set(executors)),
            }
        })
    logger.info("x-api-key: %s, data: %s" % (token, request.json))
    return json({'received': True, 'message': body.model_dump()})


@app.route('/arcee/v2/tasks/<task_id>/run', methods=["GET", ],
           ctx_label='token')
async def get_task_runs(request, task_id):
    """
    Gets task runs by task task_id
    """
    token = request.ctx.token
    o = await db.task.find_one(
        {"token": token, "_id": task_id, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    pipeline = [
        {"$match": {"task_id": task_id}},
        {
            "$lookup": {
                "from": "task",
                "localField": "task_id",
                "foreignField": "_id",
                "as": "task"
            }
        },
        {
            "$unwind": '$task'
        },
        {"$sort": {"start": -1}}
    ]
    cur = db.run.aggregate(pipeline)
    runs = [i async for i in cur]
    for run in runs:
        run["reached_goals"] = await reached_goals(run)
        run.pop("task", None)
    return json(runs)


@app.route('/arcee/v2/runs', methods=["GET", ], ctx_label='token')
async def get_runs(request):
    """
    List runs. runset_id is required when called with cluster secret
    """
    token = request.ctx.token

    runset_ids = request.args.getlist("runset_id")
    if runset_ids:
        match_q = {"$match": {"runset_id": {"$in": runset_ids}}}
    else:
        task_ids = await db.task.distinct(
            "_id", {"token": token, "deleted_at": 0})
        match_q = {"$match": {"task_id": {"$in": list(task_ids)}}}

    pipeline = [
        match_q,
        {
            "$lookup": {
                "from": "task",
                "localField": "task_id",
                "foreignField": "_id",
                "as": "task"
            }
        },
        {
            "$unwind": '$task'
        },
        {"$sort": {"start": -1}}
    ]
    cur = db.run.aggregate(pipeline)
    runs = [i async for i in cur]
    for run in runs:
        run["reached_goals"] = await reached_goals(run)
        run.pop("task", None)
    return json(runs)


@app.route('/arcee/v2/tasks/<task_id>/runs/bulk',
           methods=["GET", ], ctx_label='token')
async def bulk_get_runs(request, task_id: str):
    """
    Bulk get runs by run ids
    """
    token = request.ctx.token
    run_ids = request.args.getlist("run_id")
    if not run_ids:
        raise SanicException("run_ids is required", status_code=400)
    o = await db.task.find_one(
        {"token": token, "_id": task_id, "deleted_at": 0})
    if not o:
        raise SanicException("Task not found", status_code=404)
    metrics = await _get_task_metrics(db, task_id)
    pipeline = [
        {
            "$match": {
                "_id": {
                    "$in": run_ids
                },
                "task_id": task_id
            }
        },
        {
            "$lookup": {
                "from": "dataset",
                "localField": "dataset_id",
                "foreignField": "_id",
                "as": "dataset"
            }
        },
        {
            "$unwind": {
                "path": "$dataset",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
         "$project": {
                "_id": 1,
                "name": 1,
                "runset_id": 1,
                "runset_name": 1,
                "finish": 1,
                "tags": 1,
                "hyperparameters": 1,
                "state": 1,
                "task_id": 1,
                "start": 1,
                "number": 1,
                "deleted_at": 1,
                "dataset": 1,
                "data": 1
         },
        }
    ]
    cur = db.run.aggregate(pipeline)
    res = [i async for i in cur]
    for i in res:
        ext_data = {}
        data = i.get("data", {})
        # due to dup key it's more effectively
        for k, v in data.copy().items():
            gl = metrics.get(k, {})
            ext_data[k] = {
                "name": gl.get("name"),
                "value": v,
                "func": gl.get("func")
            }
        # replace the data
        i["data"] = ext_data
        ds = i.get("dataset")
        if ds:
            ds["id"] = ds["_id"]
            ds.pop("_id")
            ds.pop("token")
    return json(res)


@app.route('/arcee/v2/run/<run_id>', methods=["DELETE", ], ctx_label='token')
async def delete_run(request, run_id: str):
    """
    deletes run
    :param request:
    :param run_id:
    :return:
    """
    token = request.ctx.token
    run = await db.run.find_one({"_id": run_id})
    if not run:
        raise SanicException("Not found", status_code=404)
    await check_task(token, run)

    now = int(datetime.now(tz=timezone.utc).timestamp())
    await db.console.delete_many({'run_id': run['_id']})
    await db.log.delete_many({'run_id': run['_id']})
    await db.stage.delete_many({'run_id': run['_id']})
    await db.milestone.delete_many({'run_id': run['_id']})
    await db.proc_data.delete_many({'run_id': run['_id']})
    await db.artifact.delete_many({'run_id': run['_id']})
    await db.model_version.update_many({'run_id': run['_id'], 'deleted_at': 0},
                                       {'$set': {'deleted_at': now}})
    await db.run.delete_one({'_id': run_id})
    return json({"deleted": True, "_id": run_id})


async def _create_metric(**kwargs):
    metric = Metric(**kwargs).model_dump(by_alias=True)
    await db.metric.insert_one(metric)
    return metric


@app.route('/arcee/v2/metrics', methods=["POST", ], ctx_label='token')
@validate(json=MetricPostIn)
async def create_metric(request, body: MetricPostIn):
    """
    create project metric
    :param request:
    :param body:
    :return:
    """
    token = request.ctx.token
    metric = await db.metric.find_one({"token": token, "key": body.key})
    if metric:
        raise SanicException("Conflict", status_code=409)
    metric = await _create_metric(
        token=token, **body.model_dump(exclude_unset=True))
    return json(metric)


@app.route('/arcee/v2/metrics/', methods=["GET", ], ctx_label='token')
async def get_metrics(request):
    """
    get metrics
    :param request:
    :return:
    """
    token = request.ctx.token
    res = [doc async for doc in db.metric.find({"token": token})]
    return json(res)


@app.route('/arcee/v2/metrics/<metric_id>', methods=["GET", ],
           ctx_label='token')
async def get_metric(request, metric_id: str):
    """
    get metric
    :param request:
    :param metric_id:
    :return:
    """
    token = request.ctx.token
    o = await db.metric.find_one({"token": token, "_id": metric_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    return json(o)


async def _metric_used_in_lb(db_, metric_id: str, task_id: str = None):
    match_block = [
        {"deleted_at": {"$eq": 0}},
        {
            "$expr": {
                "$or": [
                    {"$eq": ["$primary_metric", "$$metricId"]},
                    {"$in": ["$$metricId",
                             {"$ifNull": ["$other_metrics", []]}]}
                ]
            }
        }]
    lb_match_block = match_block.copy()
    if task_id:
        lb_match_block.append({'task_id': task_id})
    pipeline = [
        {
            "$match": {
                "_id": metric_id
            }
        },
        {
            "$lookup": {
                "from": "leaderboard",
                "let": {"metricId": "$_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$and": lb_match_block
                        }
                    },
                    {
                        "$project": {"_id": 1}
                    }
                ],
                "as": "used_in_leaderboard"
            }
        },
        {
            "$lookup": {
                "from": "leaderboard_dataset",
                "let": {"metricId": "$_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$and": match_block
                        }
                    },
                    {
                        "$project": {"_id": 1}
                    }
                ],
                "as": "used_in_leaderboard_dataset"
            }
        },
        {
            "$project": {
                "metric_used": {
                    "$sum": [{"$size": "$used_in_leaderboard"},
                             {"$size": "$used_in_leaderboard_dataset"}]}
            }
        }
    ]
    cur = db_.metric.aggregate(pipeline)
    try:
        ri = await cur.next()
    except StopAsyncIteration:
        return False
    return bool(ri.get("metric_used", 0))


@app.route('/arcee/v2/metrics/<metric_id>', methods=["DELETE", ],
           ctx_label='token')
async def delete_metric(request, metric_id: str):
    """
    deletes metric
    :param request:
    :param metric_id:
    :return:
    """
    token = request.ctx.token
    o = await db.metric.find_one({"token": token, "_id": metric_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    if await _metric_used_in_lb(db, metric_id):
        raise SanicException("Metric used in leaderboard", status_code=409)
    await db.metric.delete_one({'_id': metric_id})
    return json({"deleted": True, "_id": metric_id})


@app.route('/arcee/v2/run/<run_id>/logs', methods=["GET", ], ctx_label='token')
async def get_logs(request, run_id: str):
    """
    get logs for run
    :param request:
    :param run_id
    :return:
    """
    token = request.ctx.token
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_task(token, o)
    res = [doc async for doc in db.log.find({"run_id": run_id})]
    return json(res)


@app.route('/arcee/v2/metrics/<metric_id>', methods=["PATCH", ],
           ctx_label='token')
@validate(json=MetricPatchIn)
async def change_metric(request, body: MetricPatchIn, metric_id: str):
    """
    update project metric
    :param request:
    :param body:
    :param metric_id:
    :return:
    """
    token = request.ctx.token
    metric = await db.metric.find_one({'_id': metric_id, 'token': token})
    if not metric:
        raise SanicException("Metric not found", status_code=404)
    metric = body.model_dump(exclude_unset=True)
    if metric:
        await db.metric.update_one(
            {"_id": metric_id}, {'$set': metric})
    return json({"updated": bool(metric), "id": metric_id})


@app.route('/arcee/v2/tasks/<task_id>/imports', methods=["GET", ],
           ctx_label='token')
async def get_imports(request, task_id: str):
    """
    Gets frameworks for task
    :param request:
    :param task_id:
    :return:
    """
    token = request.ctx.token
    o = await db.task.find_one(
        {"token": token, "_id": task_id, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    pipeline = [
        {"$match": {"task_id": task_id}},
        {
            "$group": {
                "_id": task_id,
                "imports": {"$push": "$imports"}
            }
        },
        {
            "$project": {
                "key": name,
                "imports": {
                    "$reduce": {
                        "input": "$imports",
                        "initialValue": [],
                        "in": {"$setUnion": ["$$value", "$$this"]}
                    }
                }
            }
        }
    ]
    cur = db.run.aggregate(pipeline)
    try:
        r = await cur.next()
    except StopAsyncIteration:
        r = {"_id": task_id, "key": name, "imports": list()}
    return json(r)


@app.route('/arcee/v2/tokens', methods=["POST", ], ctx_label='secret')
async def create_token(request):
    """
    creates token
    :param request:
    :return:
    """
    doc = request.json
    token = doc.get("token")
    if not token:
        raise SanicException('token is required', status_code=400)
    o = await db.token.find_one({"token": token})
    if o:
        raise SanicException("Token exists", status_code=409)
    d = {
        "_id": str(uuid.uuid4()),
        "token": token,
        "created": int(datetime.utcnow().timestamp()),
        "deleted_at": 0,
    }
    await db.token.insert_one(
        d
    )
    return json(d)


@app.route('/arcee/v2/tokens/<token>', methods=["DELETE", ],
           ctx_label='secret')
async def delete_token(request, token: str):
    """
    deletes token
    :param request:
    :param token:
    :return:
    """
    token = await db.token.find_one(
        {
            "$or": [
                {"token": token},
                {"_id": token}
            ]}
    )
    if not token:
        raise SanicException("Not found", status_code=404)
    token_id = token["_id"]
    await db.token.update_one(
        {"_id": token_id}, {
            '$set': {
                "deleted_at": int(
                    datetime.utcnow().timestamp()),
            }
        })
    return json({"deleted": True, "id": token_id})


@app.route('/arcee/v2/tokens/<token>', methods=["GET", ], ctx_label='secret')
async def get_token(request, token: str):
    """
    get token
    :param request:
    :param token:
    :return:
    """
    token = await db.token.find_one({
        "$and": [
            {"deleted_at": 0},
            {
                "$or": [
                    {"token": token},
                    {"_id": token}
                ]
            }
        ]
    })
    if not token:
        raise SanicException("Not found", status_code=404)
    return json(token)


@app.route('/arcee/v2/run/<run_id>/stages', methods=["POST", ],
           ctx_label='token')
async def create_stage(request, run_id: str):
    """
    create project run stage
    :param request:
    :param run_id: str
    :return:
    """
    token = request.ctx.token
    doc = request.json
    stage_name = doc.get("stage")
    if not stage_name:
        raise SanicException("stage name is required", status_code=400)
    # find project with given name-token
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_run_state(o)
    await check_task(token, o)
    run_id = o["_id"]
    d = {
        "_id": str(uuid.uuid4()),
        "run_id": run_id,
        "timestamp": int(datetime.utcnow().timestamp()),
        "name": stage_name,
    }
    await db.stage.insert_one(
        d
    )
    return json({"id": d["_id"]})


@app.route('/arcee/v2/run/<run_id>/stages', methods=["GET", ],
           ctx_label='token')
async def get_stages(request, run_id: str):
    """
    Get stages
    :param request:
    :param run_id:
    :return:
    """
    token = request.ctx.token
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_task(token, o)
    res = [doc async for doc in db.stage.find({"run_id": run_id})]
    return json(res)


@app.route('/arcee/v2/run/<run_id>/proc', methods=["POST", ],
           ctx_label='token')
async def create_proc_data(request, run_id: str):
    """
    create proc data log
    :param request:
    :param run_id: str
    :return:
    """
    token = request.ctx.token
    doc = request.json
    # TODO: validators
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_task(token, o)
    run_id = o["_id"]
    # Collect platform data
    platform = doc.pop("platform", {})
    instance = platform.get("instance_id")
    if instance:
        o = await db.platform.find_one({"instance_id": instance})
        if not o and platform:
            platform["_id"] = str(uuid.uuid4())
            await db.platform.insert_one(platform)
        doc["instance_id"] = instance
    proc_stats = doc.pop("proc_stats", {})
    d = {
        "_id": str(uuid.uuid4()),
        "run_id": run_id,
        "timestamp": int(datetime.utcnow().timestamp()),
        'instance_id': instance,
        "proc_stats": proc_stats,
    }
    await db.proc_data.insert_one(
        d
    )
    return json({"id": d["_id"]})


@app.route('/arcee/v2/executors/breakdown', methods=["GET", ],
           ctx_label='token')
async def get_executors_breakdown(request):
    token = request.ctx.token

    task_ids = await db.task.distinct(
        "_id", {"token": token, "deleted_at": 0})
    if not task_ids:
        return json({})

    pipeline = [
        {"$match": {"task_id": {"$in": task_ids}}},
        {"$project": {
            "_id": 0,
            "timestamp": "$start",
            "executor": "$executors"
        }},
        {"$unwind": '$executor'}
    ]
    ts_executors = defaultdict(list)
    async for data in db.run.aggregate(pipeline):
        dt = datetime.fromtimestamp(data['timestamp']).replace(
            hour=0, minute=0, second=0, microsecond=0,
            tzinfo=timezone.utc)
        ts_executors[int(dt.timestamp())].append(data['executor'])

    breakdown = {}
    if ts_executors:
        min_ts = min(ts_executors.keys())
        max_ts = max(ts_executors.keys())
        for ts in range(min_ts, max_ts + DAY_IN_SEC, DAY_IN_SEC):
            breakdown[ts] = len(set(ts_executors.get(ts, [])))
    return json(breakdown)


@app.route('/arcee/v2/run/<run_id>/proc', methods=["GET", ], ctx_label='token')
async def get_proc_data(request, run_id: str):
    """
    Get proc data for run
    :param request:
    :param run_id:
    :return:
    """
    token = request.ctx.token
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_task(token, o)
    res = [doc async for doc in db.proc_data.find({"run_id": run_id})]
    return json(res)


@app.route('/arcee/v2/executors/<executor_id>/runs', methods=["GET", ],
           ctx_label='secret')
async def get_run_ids_by_executor(request, executor_id: str):
    """
     Gets Run Ids by executor id
    :param request:
    :param executor_id: str
    :return:
    """
    task_id = "task_id"
    task_ids = list()
    supported_keys = [task_id]
    not_supported = list((filter(
        lambda x: x not in supported_keys, request.args.keys())))
    if not_supported:
        raise SanicException(
            "%s keys are not supported" % ','.join(not_supported),
            status_code=400)
    if task_id in request.args.keys():
        task_ids = request.args[task_id]
    run_ids = await db.proc_data.distinct("run_id",
                                          {"instance_id": executor_id})
    if task_ids:
        task_run_ids = [
            doc["_id"] async for doc in db.run.find(
                {"task_id": {"$in": task_ids}})
        ]
        run_ids = list(set(run_ids) & set(task_run_ids))
    return json(run_ids)


async def _create_leaderboard(**kwargs):
    lb = Leaderboard(**kwargs).model_dump(by_alias=True)
    await db.leaderboard.insert_one(lb)
    return lb


@app.route('/arcee/v2/tasks/<task_id>/leaderboards',
           methods=["POST", ], ctx_label='token')
@validate(json=LeaderboardPostIn)
async def create_leaderboard(request, body: LeaderboardPostIn,
                             task_id: str):
    """
    create leaderboard
    :param request:
    :param body:
    :param task_id: str
    :return:
    """
    token = request.ctx.token
    task = await db.task.find_one({
        '_id': task_id, 'token': token, 'deleted_at': 0})
    if not task:
        raise SanicException("Task not found", status_code=404)
    lb = await db.leaderboard.find_one({
        'task_id': task_id, 'token': token, 'deleted_at': 0
    })
    if lb:
        raise SanicException("Conflict", status_code=409)
    await check_metrics(body.metrics)
    leaderboard = await _create_leaderboard(
        token=token, task_id=task_id,
        **body.model_dump(exclude_unset=True))
    return json(leaderboard, status=201)


async def _create_leaderboard_dataset(**kwargs) -> dict:
    LeaderboardDataset.remove_dup_ds_ids(kwargs)
    d = LeaderboardDataset(**kwargs).model_dump(by_alias=True)
    await db.leaderboard_dataset.insert_one(d)
    return d


@app.route('/arcee/v2/leaderboards/<leaderboard_id>/leaderboard_datasets',
           methods=["POST", ], ctx_label='token')
@validate(json=LeaderboardDatasetPostIn)
async def create_leaderboard_dataset(request, body: LeaderboardDatasetPostIn,
                                     leaderboard_id: str):
    token = request.ctx.token

    leaderboard = await db.leaderboard.find_one(
        {"token": token, "_id": leaderboard_id, "deleted_at": 0})
    if not leaderboard:
        raise SanicException("Leaderboard not found", status_code=404)
    d = await _create_leaderboard_dataset(
        token=token, leaderboard_id=leaderboard_id, **body.model_dump())
    return json(d, status=201)


@app.route('/arcee/v2/leaderboard_datasets/<id_>', methods=["GET", ],
           ctx_label='token')
async def get_leaderboard_dataset(request, id_: str):
    token = request.ctx.token
    d = await db.leaderboard_dataset.find_one(
        {"$and": [
            {"token": token},
            {"_id": id_},
            {"deleted_at": 0}
        ]})
    if not d:
        raise SanicException("LeaderboardDataset not found", status_code=404)
    pipeline = [
        {
            "$match":
                {
                    "$and": [
                        {"token": token},
                        {"_id": id_},
                        {"deleted_at": 0}
                    ]
                }
        },
        {
            "$lookup": {
                "from": "dataset",
                "localField": "dataset_ids",
                "foreignField": "_id",
                "as": "datasets"
            }
        },
    ]
    cur = db.leaderboard_dataset.aggregate(pipeline)
    return json(await cur.next())


@app.route('/arcee/v2/leaderboards/<leaderboard_id>/leaderboard_datasets',
           methods=["GET", ], ctx_label='token')
async def get_leaderboard_datasets(request, leaderboard_id: str):
    token = request.ctx.token
    match_filter = {
        "leaderboard_id": leaderboard_id,
        "token": token,
        "deleted_at": 0
    }
    include_deleted = "include_deleted"
    if (include_deleted in request.args.keys() and
            await to_bool(request.args.get(include_deleted))):
        match_filter.pop('deleted_at')
    pipeline = [
        {
            "$match": match_filter
        },
        {
            "$lookup": {
                "from": "metric",
                "localField": "primary_metric",
                "foreignField": "_id",
                "as": "primary_metric"
            }
        },
        {
            "$unwind": "$primary_metric"
        },
        {
            "$project": {
                "leaderboard": 0,
                "primary_metric._id": 0,
                "primary_metric.token": 0
            }
        },
    ]
    cur = db.leaderboard_dataset.aggregate(pipeline)
    result = []
    leaderboard = None
    tendency = None
    key = None
    func = None
    async for leaderboard_dataset in cur:
        # candidates (1-st level groups) are basically the same for all
        # leaderboard datasets, so generate leaderboard once to use it as
        # a list of candidates
        if not leaderboard:
            leaderboard = await get_calculated_leaderboard(
                db, token, leaderboard_dataset['_id'])

        # primary_metric is the same for all leaderboard datasets
        if not tendency:
            tendency = leaderboard_dataset['primary_metric']['tendency']
        if not key:
            key = leaderboard_dataset['primary_metric']['key']
        if not func:
            func = leaderboard_dataset['primary_metric']['func']

        lb_dataset_ids = leaderboard_dataset['dataset_ids']

        best_score = None
        for cand in leaderboard:
            # get primary metric value for group according to datasets ids
            cand_score = None
            qualification = set(cand['dataset_ids']) & set(lb_dataset_ids)

            if set(lb_dataset_ids) == set(cand['qualification']):
                # primary metric for current LB dataset is already calculated
                cand_score = cand['primary_metric'][key]['value']
            elif not lb_dataset_ids or qualification == set(lb_dataset_ids):
                # group is not qualified by required datasets, but contains
                # some suitable runs
                runs = cand['run_ids']
                pipeline = [
                    {'$match': {'_id': {'$in': runs}}},
                    {'$group': {'_id': None,
                                'score': {'$%s' % func: '$data.%s' % key}}},
                ]
                if lb_dataset_ids:
                    pipeline[0]['$match'].update(
                        {'dataset_id': {'$in': lb_dataset_ids}})
                res = db.run.aggregate(pipeline)
                try:
                    r = await res.next()
                except StopAsyncIteration:
                    r = {'score': None}
                cand_score = r['score']
            if cand_score and (not best_score or (
                    tendency == Tendencies.MORE.value and
                    best_score < cand_score) or (
                    tendency == Tendencies.LESS.value and
                    best_score > cand_score)):
                best_score = cand_score
        leaderboard_dataset['primary_metric']['value'] = best_score
        result.append(leaderboard_dataset)
    return json(result)


@app.route('/arcee/v2/leaderboard_datasets/<id_>', methods=["PATCH", ],
           ctx_label='token')
@validate(json=LeaderboardDatasetPatchIn)
async def update_leaderboard_dataset(request, body: LeaderboardDatasetPatchIn,
                                     id_: str):
    token = request.ctx.token
    o = await db.leaderboard_dataset.find_one(
        {"$and": [
            {"token": token},
            {"_id": id_},
            {"deleted_at": 0}
        ]})
    if not o:
        raise SanicException("LeaderboardDataset not found", status_code=404)
    d = body.model_dump(exclude_unset=True)
    if d:
        await check_leaderboard_filters(o, d)
        LeaderboardDatasetPatchIn.remove_dup_ds_ids(d)
        await db.leaderboard_dataset.update_one(
            {"_id": id_}, {'$set': d})
    o = await db.leaderboard_dataset.find_one({"_id": id_})
    return json(o)


@app.route('/arcee/v2/leaderboard_datasets/<id_>', methods=["DELETE", ],
           ctx_label='token')
async def delete_leaderboard_dataset(request, id_: str):
    token = request.ctx.token
    o = await db.leaderboard_dataset.find_one({"token": token, "_id": id_})
    if not o:
        raise SanicException("LeaderboardDataset not found", status_code=404)
    await db.leaderboard_dataset.update_one({"_id": id_}, {'$set': {
        "deleted_at": int(datetime.utcnow().timestamp())
    }})
    return json('', status=204)


@app.route('/arcee/v2/leaderboard_datasets/<id_>/details', methods=["GET", ],
           ctx_label='token')
async def get_leaderboard_dataset_details(request, id_: str):
    token = request.ctx.token
    o = await db.leaderboard_dataset.find_one(
        {"$and": [
            {"token": token},
            {"_id": id_},
            {"deleted_at": 0}
        ]})
    if not o:
        raise SanicException("LeaderboardDataset not found", status_code=404)
    # get coverage
    ids = o['dataset_ids']
    pipeline = [
        {
            "$match": {
                "_id": {"$in": ids},
                "token": token,
                "deleted_at": {"$eq": 0},
            }
        },
        {"$sort": {"created_at": -1}},
        {
            "$lookup": {
                "from": "run",
                "as": "run_data",
                "let": {"dsid": "$_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$dataset_id", "$$dsid"]},
                                    {"$eq": ["$state", 2]},
                                ]
                            }
                        }
                    },
                    {"$sort": {"start": -1}},
                    {"$limit": 1},
                ],
            }
        },
        {"$unwind": "$run_data"},
    ]

    cur = db.dataset.aggregate(pipeline)
    res = [i async for i in cur]
    return json(res)


@app.route('/arcee/v2/tasks/<task_id>/leaderboards',
           methods=["GET", ], ctx_label='token')
async def get_leaderboard(request, task_id: str):
    """
    get leaderboard
    :param request:
    :param task_id: str
    :return:
    """
    response = {}
    token = request.ctx.token
    leaderboard = await db.leaderboard.find_one(
        {"token": token, "task_id": task_id, "deleted_at": 0})
    if leaderboard:
        response = leaderboard
    return json(response)


@app.route('/arcee/v2/leaderboards/<leaderboard_id>',
           methods=["GET", ], ctx_label='token')
async def get_leaderboard_by_id(request, leaderboard_id: str):
    """
    get leaderboard
    :param request:
    :param leaderboard_id: str
    :return:
    """
    response = {}
    token = request.ctx.token
    leaderboard = await db.leaderboard.find_one(
        {"token": token, "_id": leaderboard_id, "deleted_at": 0})
    if leaderboard:
        response = leaderboard
    return json(response)


@app.route('/arcee/v2/tasks/<task_id>/leaderboards',
           methods=["PATCH", ], ctx_label='token')
@validate(json=LeaderboardPatchIn)
async def change_leaderboard(request, body: LeaderboardPatchIn,
                             task_id: str):
    """
    update leaderboard
    :param request:
    :param body:
    :param task_id: str
    :return:
    """
    token = request.ctx.token
    task = await db.task.find_one({
        '_id': task_id, 'token': token, 'deleted_at': 0})
    if not task:
        raise SanicException("Task not found", status_code=404)
    o = await db.leaderboard.find_one(
        {"$and": [
            {"token": token},
            {"task_id": task_id},
            {"deleted_at": 0}
        ]})
    if not o:
        raise SanicException("Leaderboard not found", status_code=404)
    lb_id = o['_id']
    await check_metrics(body.metrics)
    lb = body.model_dump(exclude_unset=True)
    if lb:
        await check_leaderboard_filters(o, lb)
        await db.leaderboard.update_one(
            {"_id": lb_id}, {'$set': lb})
    o = await db.leaderboard.find_one({"_id": lb_id})
    return json(Leaderboard(**o).model_dump(by_alias=True))


@app.route('/arcee/v2/tasks/<task_id>/leaderboards',
           methods=["DELETE", ], ctx_label='token')
async def delete_leaderboard(request, task_id: str):
    """
    deletes leaderboard
    :param request:
    :param task_id: str
    :return:
    """
    token = request.ctx.token
    leaderboard = await db.leaderboard.find_one(
        {"token": token, "task_id": task_id, "deleted_at": 0})
    if not leaderboard:
        raise SanicException("Not found", status_code=404)
    deleted_at = int(datetime.now(tz=timezone.utc).timestamp())
    await db.leaderboard_dataset.update_many(
        {"leaderboard_id": leaderboard["_id"]},
        {'$set': {'deleted_at': deleted_at}}
    )
    await db.leaderboard.update_one(
        {"_id": leaderboard['_id']},
        {'$set': {'deleted_at': deleted_at}}
    )
    return json({"deleted": True, "_id": leaderboard['_id']})


@app.route('/arcee/v2/leaderboard_datasets/<leaderboard_dataset_id>/generate',
           methods=["GET", ], ctx_label='token')
async def leaderboard_details(request, leaderboard_dataset_id: str):
    """
    Calculate leaderboard
    :param request:
    :param leaderboard_dataset_id: str
    :return:
    """
    token = request.ctx.token
    lb = await get_calculated_leaderboard(db, token, leaderboard_dataset_id)
    return json(lb)


async def _create_dataset(**kwargs) -> dict:
    d = Dataset(**kwargs).model_dump(by_alias=True)
    await db.dataset.insert_one(d)
    return d


@app.route('/arcee/v2/datasets', methods=["POST", ], ctx_label='token')
@validate(json=DatasetPostIn)
async def create_dataset(request, body: DatasetPostIn):
    token = request.ctx.token
    o = await db.dataset.find_one(
        {"$and": [
            {"token": token},
            {"path": body.path},
            {"deleted_at": 0}
        ]})
    if o:
        raise SanicException("Dataset exists", status_code=409)
    d = await _create_dataset(
        token=token, **body.model_dump(exclude_unset=True))
    return json(d, status=201)


@app.route("/arcee/v2/run/<run_id>/dataset_register", methods=["POST", ],
           ctx_label='token')
@validate(json=DatasetPostIn)
async def register_dataset(request, body: DatasetPostIn, run_id: str):
    token = request.ctx.token
    run = await db.run.find_one({"_id": run_id})
    if not run:
        raise SanicException("Run not found", status_code=404)
    d = await db.dataset.find_one(
        {"$and": [
            {"token": token},
            {"path": body.path},
            {"deleted_at": 0}
        ]})
    if not d:
        d = await _create_dataset(
            token=token, **body.model_dump(exclude_unset=True))
    await db.run.update_one(
        {"_id": run_id}, {"$set": {"dataset_id": d["_id"]}})
    return json({"id": d["_id"]})


@app.route('/arcee/v2/datasets', methods=["GET", ], ctx_label='token')
async def get_datasets(request):
    token = request.ctx.token
    dataset_ids = request.args.getlist("dataset_id")
    match_filter = {
        "token": token,
        "deleted_at": 0
    }
    if dataset_ids:
        match_filter.update({'_id': {'$in': dataset_ids}})
    # TODO: possibly move to bulk_get API with ability to get deleted objects
    include_deleted = "include_deleted"
    if (include_deleted in request.args.keys() and
            await to_bool(request.args.get(include_deleted))):
        match_filter.pop('deleted_at')
    res = [Dataset(**doc).model_dump(by_alias=True)
           async for doc in db.dataset.find(match_filter)]
    return json(res)


@app.route('/arcee/v2/datasets/<id_>', methods=["GET", ], ctx_label='token')
async def get_dataset(request, id_: str):
    token = request.ctx.token
    d = await db.dataset.find_one(
        {"$and": [
            {"token": token},
            {"_id": id_},
            {"deleted_at": 0}
        ]})
    if not d:
        raise SanicException("Dataset not found", status_code=404)
    return json(Dataset(**d).model_dump(by_alias=True))


@app.route('/arcee/v2/datasets/<id_>', methods=["PATCH", ], ctx_label='token')
@validate(json=DatasetPatchIn)
async def update_dataset(request, body: DatasetPatchIn, id_: str):
    token = request.ctx.token
    o = await db.dataset.find_one(
        {"$and": [
            {"token": token},
            {"_id": id_},
            {"deleted_at": 0}
        ]})
    if not o:
        raise SanicException("Dataset not found", status_code=404)
    d = body.model_dump(exclude_unset=True)
    if d:
        await db.dataset.update_one(
            {"_id": id_}, {'$set': d})
    o = await db.dataset.find_one({"_id": id_})
    return json(Dataset(**o).model_dump(by_alias=True))


async def _dataset_used_in_leaderboard(db_, dataset_id: str):
    pipeline = [
        {
            "$match": {
                "_id": dataset_id
            }
        },
        {
            "$lookup": {
                "from": "leaderboard_dataset",
                "let": {"dataset_id": "$_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$in": ["$$dataset_id", "$dataset_ids"]},
                                    {"$eq": ["$deleted_at", 0]}
                                ]
                            }
                        }
                    }
                ],
                "as": "leaderboard_info"
            }
        },
        {
            "$addFields": {
                "used": {
                    "$cond": {
                        "if": {"$gt": [{"$size": "$leaderboard_info"}, 0]},
                        "then": True,
                        "else": False
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "used": 1
            }
        }
    ]
    cur = db_.dataset.aggregate(pipeline)
    try:
        ri = await cur.next()
    except StopAsyncIteration:
        return False
    return ri.get("used", False)


@app.route('/arcee/v2/datasets/<id_>', methods=["DELETE", ], ctx_label='token')
async def delete_dataset(request, id_: str):
    token = request.ctx.token
    o = await db.dataset.find_one({"token": token, "_id": id_})
    if not o:
        raise SanicException("Dataset not found", status_code=404)
    if await _dataset_used_in_leaderboard(db, id_):
        raise SanicException("Dataset used in leaderboard", status_code=409)
    await db.dataset.update_one({"_id": id_}, {'$set': {
        "deleted_at": int(datetime.utcnow().timestamp())
    }})
    return json('', status=204)


@app.route('/arcee/v2/labels', methods=["GET", ], ctx_label='token')
async def get_labels(request):
    token = request.ctx.token
    pipeline = [
        {"$match": {"token": token, "deleted_at": 0}},
        {"$sort": {"created_at": -1}},
        {"$unwind": "$labels"},
        {"$group": {"_id": None, "labels": {"$push": "$labels"}}},
    ]
    labels = []
    cur = db.dataset.aggregate(pipeline)
    try:
        res = await cur.next()
    except StopAsyncIteration:
        pass
    else:
        # keep insertion order
        labels.extend(OrderedDict.fromkeys(res.get('labels', [])).keys())
    return json(labels)


@app.route('/arcee/v2/tasks/<task_id>/tags', methods=["GET", ],
           ctx_label='token')
async def get_tags(request, task_id: str):
    token = request.ctx.token
    task = await db.task.find_one(
        {'_id': task_id, 'token': token, 'deleted_at': 0})
    if not task:
        raise SanicException("Task not found", status_code=404)
    pipeline = [
        {"$match": {"task_id": task_id, "deleted_at": 0}},
        {"$project": {"tags": {"$objectToArray": "$tags"}}},
        {"$unwind": "$tags"},
        {"$group": {"_id": None, "tags": {"$addToSet": "$tags.k"}}},
    ]
    tags = []
    cur = db.run.aggregate(pipeline)
    try:
        res = await cur.next()
        tags = list(res['tags'])
    except StopAsyncIteration:
        pass
    return json(tags)


@app.route('/arcee/v2/run/<run_id>/consoles', methods=["POST", ],
           ctx_label='token')
@validate(json=ConsolePostIn)
async def create_run_console(request, body: ConsolePostIn, run_id: str):
    token = request.ctx.token
    run = await db.run.find_one({"_id": run_id})
    if not run:
        raise SanicException("Not found", status_code=404)
    await check_run_state(run)
    await check_task(token, run)
    c = await db.console.find_one({"run_id": run_id})
    if c:
        raise SanicException("Console exists", status_code=409)
    console = Console(run_id=run["_id"], **body.model_dump())
    default_output_length = 512 * 1024
    for prop in ['output', 'error']:
        val = getattr(console, prop, None)
        if val and len(val) > default_output_length:
            setattr(console, prop, val[:default_output_length])
    await db.console.insert_one(
        console.model_dump(by_alias=True)
    )
    return json({"id": console.id})


@app.route('/arcee/v2/run/<run_id>/console', methods=["GET", ],
           ctx_label='token')
async def get_run_console(request, run_id: str):
    token = request.ctx.token
    console = await db.console.find_one(
        {"run_id": run_id})
    if not console:
        raise SanicException("Not found", status_code=404)
    return json(console)


async def _create_model(**kwargs) -> dict:
    model = Model(**kwargs).model_dump(by_alias=True)
    await db.model.insert_one(model)
    return model


@app.route('/arcee/v2/models', methods=["POST", ], ctx_label='token')
@validate(json=ModelPostIn)
async def create_model(request, body: ModelPostIn):
    token = request.ctx.token
    model = await db.model.find_one(
        {"$and": [
            {"token": token},
            {"key": body.key}
        ]})
    if not model:
        model = await _create_model(
            token=token, **body.model_dump(exclude_unset=True))
    return json(model, status=201)


async def _get_aliased_versions(db_, model_ids, max_aliased_versions):
    pipeline = [
        # find model_versions with aliases
        {'$match': {
            'model_id': {'$in': model_ids},
            'deleted_at': 0,
            'aliases': {'$ne': []}
        }},
        {'$sort': {'created_at': -1}},
        {'$unwind': '$aliases'},
        # collect all ids of aliased model_version by model
        {'$group': {
            '_id': '$model_id',
            'alias_version_id': {'$push': '$_id'}}},
        # get first max_aliased_versions model versions ids
        {'$project': {
            '_id': '$_id',
            'alias_version_id': {
                '$slice': ['$alias_version_id', max_aliased_versions]}}},
        {'$unwind': '$alias_version_id'},
        # replace model_version ids by model_version rows
        {'$lookup': {
            'from': 'model_version',
            'localField': 'alias_version_id',
            'foreignField': '_id',
            'as': 'model_version'}},
        {'$unwind': '$model_version'},
        {'$replaceRoot': {'newRoot': '$model_version'}},
    ]
    versions = [
        version async for version in db_.model_version.aggregate(pipeline)
    ]
    # remove duplicates
    return [
        x for i, x in enumerate(versions) if x not in versions[i+1:]
    ]


async def _get_last_versions_map(db_, model_ids):
    pipeline = [
        {'$match': {
            'model_id': {'$in': model_ids},
            'deleted_at': 0}},
        {'$sort': {'created_at': -1}},
        {'$group': {
            '_id': '$model_id',
            'version_id': {'$first': '$_id'}}},
        {'$lookup': {
            'from': 'model_version',
            'localField': 'version_id',
            'foreignField': '_id',
            'as': 'model_version'}},
        {'$unwind': '$model_version'}
    ]
    versions = [
        version async for version in db_.model_version.aggregate(pipeline)
    ]
    return {x['_id']: x['model_version'] for x in versions}


@app.route('/arcee/v2/models', methods=["GET", ], ctx_label='token')
async def list_models(request):
    token = request.ctx.token
    max_aliased_versions = 20
    result = [Model(**doc).model_dump(by_alias=True)
              async for doc in db.model.find({'token': token}).sort(
                  [('created_at', -1)])]
    model_ids = [x['_id'] for x in result]
    aliased_versions = await _get_aliased_versions(
        db, model_ids, max_aliased_versions)
    model_aliased_versions = defaultdict(list)
    for version in aliased_versions:
        model_id = version['model_id']
        for alias in version['aliases']:
            if len(model_aliased_versions[model_id]) >= max_aliased_versions:
                break
            updated_version = version.copy()
            updated_version['alias'] = alias
            model_aliased_versions[model_id].append(updated_version)
    last_versions_map = await _get_last_versions_map(db, model_ids)
    for model_dict in result:
        model_id = model_dict['_id']
        model_dict['aliased_versions'] = model_aliased_versions.get(
            model_id, [])
        model_dict['last_version'] = last_versions_map.get(model_id, {})
    return json(result)


async def _get_model(token, model_id):
    model = await db.model.find_one(
        {"$and": [
            {"token": token},
            {"_id": model_id}
        ]})
    if not model:
        raise SanicException("Model not found", status_code=404)
    return model


@app.route('/arcee/v2/models/<id_>', methods=["GET", ], ctx_label='token')
async def get_model(request, id_: str):
    model = await _get_model(request.ctx.token, id_)
    model_dict = Model(**model).model_dump(by_alias=True)
    versions_list = [ModelVersion(**x) async
                     for x in db.model_version.find(
                         {'model_id': id_, 'deleted_at': 0})]
    versions_list.sort(key=lambda x: x.created_at, reverse=True)
    runs_ids = [x.run_id for x in versions_list]
    runs_map = {}
    for i in range(0, len(runs_ids), CHUNK_SIZE):
        runs_chunk = runs_ids[i:i+CHUNK_SIZE]
        runs_map.update({x['_id']: x async for x in db.run.aggregate([
            {'$match': {'_id': {'$in': runs_chunk}}},
            {'$lookup': {
                'from': 'task',
                'localField': 'task_id',
                'foreignField': '_id',
                'as': 'task_name'}},
            {'$unwind': '$task_name'},
            {'$project': {
                '_id': 1,
                'name': 1,
                'number': 1,
                'task_id': 1,
                'task_name': '$task_name.name'
            }}
        ])})
    model_dict['versions'] = []
    for version in versions_list:
        version_dict = version.model_dump(
            include=['id', 'version', 'path', 'aliases', 'tags', 'created_at'],
            by_alias=True)
        version_dict['run'] = runs_map.get(version.run_id, {})
        model_dict['versions'].append(version_dict)
    return json(model_dict)


@app.route('/arcee/v2/models/<id_>', methods=["PATCH", ], ctx_label='token')
@validate(json=ModelPatchIn)
async def update_model(request, body: ModelPatchIn, id_: str):
    token = request.ctx.token
    await _get_model(token, id_)
    model = body.model_dump(exclude_unset=True)
    if model:
        await db.model.update_one(
            {"_id": id_}, {'$set': model})
    obj = await db.model.find_one({"_id": id_})
    return json(Model(**obj).model_dump(by_alias=True))


@app.route('/arcee/v2/models/<id_>', methods=["DELETE", ], ctx_label='token')
async def delete_model(request, id_: str):
    await _get_model(request.ctx.token, id_)
    await db.model_version.delete_many({"model_id": id_})
    await db.model.delete_one({"_id": id_})
    return json({'deleted': True, '_id': id_}, status=204)


async def _create_model_version(**kwargs) -> dict:
    model = ModelVersion(**kwargs).model_dump(by_alias=True)
    await db.model_version.insert_one(model)
    return model


async def _get_next_version(model_id, version=None, run_id=None):
    filters = {"model_id": model_id}
    if run_id:
        filters['run_id'] = {'$ne': run_id}
    versions = [x['version'] async for x in db.model_version.find(
        filters, {'version': 1})]
    if not version or (version and version in versions):
        max_version = 0
        for v in versions:
            try:
                v = int(v)
                if v > max_version:
                    max_version = v
            except ValueError:
                continue
        version = str(max_version + 1)
    return version


async def _remove_used_aliases(aliases, model_id):
    aliases_exist = [x async for x in db.model_version.find(
        {'model_id': model_id, 'aliases': {'$in': aliases}, 'deleted_at': 0}
    )]
    if aliases_exist:
        for alias in aliases_exist:
            curr_aliases = alias['aliases']
            new_aliases = list(set(curr_aliases) - set(aliases))
            await db.model_version.update_one(
                {'_id': alias['_id']}, {'$set': {'aliases': new_aliases}})


@app.route('/arcee/v2/runs/<run_id>/models/<model_id>/version',
           methods=["POST", ], ctx_label='token')
@validate(json=ModelVersionIn)
async def create_model_version(request, body: ModelVersionIn,
                               run_id: str, model_id: str):
    token = request.ctx.token
    await _get_model(token, model_id)
    run = await db.run.find_one({
        '_id': run_id
    })
    if not run:
        raise SanicException('Run not found', status_code=404)
    model_version = await db.model_version.find_one(
        {"$and": [
            {"model_id": model_id},
            {"run_id": run_id}
        ]})
    if model_version:
        raise SanicException("Model version already exists", status_code=409)
    body.version = await _get_next_version(model_id, body.version)
    if body.aliases:
        await _remove_used_aliases(body.aliases, model_id)
    model = await _create_model_version(
        run_id=run_id, model_id=model_id,
        **body.model_dump(exclude_unset=True))
    return json(model, status=201)


@app.route('/arcee/v2/runs/<run_id>/models/<model_id>/version',
           methods=["PATCH", ], ctx_label='token')
@validate(json=ModelVersionIn)
async def update_model_version(request, body: ModelVersionIn,
                               run_id: str, model_id: str):
    await _get_model(request.ctx.token, model_id)
    model_version = await db.model_version.find_one(
        {"$and": [
            {"model_id": model_id},
            {"run_id": run_id},
            {"deleted_at": 0}
        ]})
    if not model_version:
        raise SanicException("Model version not found", status_code=404)
    model_version_id = model_version['_id']
    if body.version:
        body.version = await _get_next_version(model_id, body.version, run_id)
    if body.aliases:
        await _remove_used_aliases(body.aliases, model_id)
    updates = body.model_dump(exclude_unset=True)
    if updates:
        await db.model_version.update_one(
            {"_id": model_version_id}, {'$set': updates})
    obj = await db.model_version.find_one({"_id": model_version_id})
    return json(ModelVersion(**obj).model_dump(by_alias=True))


@app.route('/arcee/v2/runs/<run_id>/models/<model_id>/version',
           methods=["DELETE", ], ctx_label='token')
async def delete_model_version(request, run_id: str, model_id: str):
    await _get_model(request.ctx.token, model_id)
    model_version = await db.model_version.find_one(
        {"$and": [
            {"model_id": model_id},
            {"run_id": run_id},
            {"deleted_at": 0}
        ]})
    if not model_version:
        raise SanicException("Model version not found", status_code=404)
    model_version_id = model_version['_id']
    await db.model_version.update_one(
        {"_id": model_version_id},
        {'$set': {
            "deleted_at": int(datetime.now(tz=timezone.utc).timestamp())}}
    )
    return json('', status=204)


@app.route('/arcee/v2/tasks/<task_id>/model_versions', methods=["GET", ],
           ctx_label='token')
async def get_model_versions_for_task(request, task_id: str):
    runs_map = {}
    task = await db.task.find_one({
        'token': request.ctx.token,
        '_id': task_id,
        'deleted_at': 0
    })
    if task:
        runs = [x async for x in db.run.find(
            {'task_id': task_id},
            {'_id': 1, 'name': 1, 'number': 1})]
        runs_map = {x['_id']: x for x in runs}
    if not runs_map:
        return json([])
    pipeline = [
        {'$match': {
            'run_id': {'$in': list(runs_map.keys())},
            'deleted_at': 0}},
        {'$sort': {'created_at': -1}},
        {
            '$lookup': {
                'from': 'model',
                'localField': 'model_id',
                'foreignField': '_id',
                'as': 'model'
            }
        },
        {'$unwind': '$model'}
    ]
    versions = [x async for x in db.model_version.aggregate(pipeline)]
    for version in versions:
        version['run'] = runs_map.get(version['run_id'], {})
        version.pop('run_id', None)
        version.pop('model_id', None)
    return json(versions)


def _format_artifact(artifact: dict, run: dict, tasks: dict = None) -> dict:
    artifact.pop('run_id', None)
    artifact['run'] = {
        '_id': run['_id'],
        'task_id': run['task_id'],
        'name': run['name'],
        'number': run['number']
    }
    if tasks:
        artifact['run']['task_name'] = tasks[run['task_id']]
    return artifact


async def _create_artifact(**kwargs) -> dict:
    artifact = Artifact(**kwargs).model_dump(by_alias=True)
    await db.artifact.insert_one(artifact)
    return artifact


@app.route('/arcee/v2/artifacts', methods=["POST", ], ctx_label='token')
@validate(json=ArtifactPostIn)
async def create_artifact(request, body: ArtifactPostIn):
    token = request.ctx.token
    run = await db.run.find_one({"_id": body.run_id, 'deleted_at': 0})
    if not run:
        raise SanicException("Run not found", status_code=404)
    artifact = await _create_artifact(
            token=token, **body.model_dump(exclude_unset=True))
    artifact = _format_artifact(artifact, run)
    return json(artifact, status=201)


def _build_artifact_filter_pipeline(run_ids: list,
                                    query: ArtifactSearchParams):
    filters = defaultdict(dict)
    filters['run_id'] = {'$in': run_ids}
    if query.created_at_lt:
        created_at_dt = int((datetime.fromtimestamp(
            query.created_at_lt) + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0).timestamp())
        filters['_created_at_dt'].update({'$lt': created_at_dt})
        filters['created_at'].update({'$lt': query.created_at_lt})
    if query.created_at_gt:
        created_at_dt = int(datetime.fromtimestamp(
            query.created_at_gt).replace(hour=0, minute=0, second=0,
                                         microsecond=0).timestamp())
        filters['_created_at_dt'].update({'$gte': created_at_dt})
        filters['created_at'].update({'$gt': query.created_at_gt})
    pipeline = [{'$match': filters}]
    if query.text_like:
        pipeline += [
            {'$addFields': {'tags_array': {'$objectToArray': '$tags'}}},
            {'$match': {'$or': [
                {'name': {'$regex': f'(.*){query.text_like}(.*)'}},
                {'description': {'$regex': f'(.*){query.text_like}(.*)'}},
                {'path': {'$regex': f'(.*){query.text_like}(.*)'}},
                {'tags_array.k': {'$regex': f'(.*){query.text_like}(.*)'}},
                {'tags_array.v': {'$regex': f'(.*){query.text_like}(.*)'}},
            ]}}
        ]
    return pipeline


@app.route('/arcee/v2/artifacts', methods=["GET", ], ctx_label='token')
async def list_artifacts(request):
    token = request.ctx.token
    try:
        query = ArtifactSearchParams(**request.args)
    except ValidationError as e:
        raise SanicException(f'Invalid query params: {str(e)}',
                             status_code=400)
    result = {
        'artifacts': [],
        'limit': query.limit,
        'start_from': query.start_from,
        'total_count': 0
    }
    task_query = {'token': token}
    if query.task_id:
        task_query['_id'] = {'$in': query.task_id}
    tasks = {x['_id']: x['name'] async for x in db.task.find(
        task_query, {'_id': 1, 'name': 1})}
    tasks_ids = list(tasks.keys())

    run_query = {'task_id': {'$in': tasks_ids}, 'deleted_at': 0}
    if query.run_id:
        run_query['_id'] = {'$in': query.run_id}
    runs_map = {run['_id']: run async for run in db.run.find(run_query)}
    runs_ids = list(runs_map.keys())

    pipeline = _build_artifact_filter_pipeline(runs_ids, query)
    pipeline.append({'$sort': {'created_at': -1, '_id': 1}})

    paginate_pipeline = [{'$skip': query.start_from}]
    if query.limit:
        paginate_pipeline.append({'$limit': query.limit})
    pipeline.extend(paginate_pipeline)
    async for artifact in db.artifact.aggregate(pipeline, allowDiskUse=True):
        artifact.pop('tags_array', None)
        res = Artifact(**artifact).model_dump(by_alias=True)
        res.pop('run_id', None)
        res = _format_artifact(artifact, runs_map[artifact['run_id']], tasks)
        result['artifacts'].append(res)
    if len(result['artifacts']) != 0 and not query.limit:
        result['total_count'] = len(result['artifacts']) + query.start_from
    else:
        pipeline = _build_artifact_filter_pipeline(runs_ids, query)
        pipeline.append({'$count': 'count'})
        res = db.artifact.aggregate(pipeline)
        try:
            count = await res.next()
            result['total_count'] = count['count']
        except StopAsyncIteration:
            pass
    return json(result)


async def _get_artifact(token, artifact_id):
    artifact = await db.artifact.find_one(
        {"$and": [
            {"token": token},
            {"_id": artifact_id}
        ]})
    if not artifact:
        raise SanicException("Artifact not found", status_code=404)
    return artifact


@app.route('/arcee/v2/artifacts/<id_>', methods=["GET", ], ctx_label='token')
async def get_artifact(request, id_: str):
    artifact = await _get_artifact(request.ctx.token, id_)
    artifact_dict = Artifact(**artifact).model_dump(by_alias=True)
    run = await db.run.find_one({"_id": artifact['run_id'], 'deleted_at': 0})
    if not run:
        raise SanicException("Run not found", status_code=404)
    artifact_dict = _format_artifact(artifact_dict, run)
    return json(artifact_dict)


@app.route('/arcee/v2/artifacts/<id_>', methods=["PATCH", ], ctx_label='token')
@validate(json=ArtifactPatchIn)
async def update_artifact(request, body: ArtifactPatchIn, id_: str):
    token = request.ctx.token
    artifact = await _get_artifact(token, id_)
    run = await db.run.find_one(
        {"_id": artifact['run_id'], 'deleted_at': 0})
    if not run:
        raise SanicException("Run not found", status_code=404)
    updates = body.model_dump(exclude_unset=True)
    if updates:
        await db.artifact.update_one(
            {"_id": id_}, {'$set': updates})
    obj = await db.artifact.find_one({"_id": id_})
    artifact = Artifact(**obj).model_dump(by_alias=True)
    artifact = _format_artifact(artifact, run)
    return json(artifact)


@app.route('/arcee/v2/artifacts/<id_>', methods=["DELETE", ],
           ctx_label='token')
async def delete_artifact(request, id_: str):
    await _get_artifact(request.ctx.token, id_)
    await db.artifact.delete_one({"_id": id_})
    return json({'deleted': True, '_id': id_}, status=204)


if __name__ == '__main__':
    logger.info('Waiting for migration lock')
    # trick to lock migrations
    with EtcdLock(
            EtcdClient(host=etcd_host, port=etcd_port), 'arcee_migrations'):
        config_params = {
            'mongo_username': name,
            'mongo_password': password,
            'mongo_url': "mongodb://{host}:{port}/admin".format(
                host=host, port=port),
            'mongo_database': db_name,
            'mongo_migrations_path': os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'migrations')
        }
        manager = MigrationManager(config=Configuration(config=config_params))
        manager.run()
    logger.info('Starting server')
    app.run(host='0.0.0.0', port=8891, access_log=False)
