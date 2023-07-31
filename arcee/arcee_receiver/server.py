import time
from datetime import datetime
import asyncio
from etcd import Lock as EtcdLock, Client as EtcdClient
from typing import Tuple
import os
import uuid

from mongodb_migrations.cli import MigrationManager
from mongodb_migrations.config import Configuration
from sanic import Sanic
from sanic.log import logger
from sanic.response import json
from sanic.exceptions import SanicException
import motor.motor_asyncio

from aconfig_cl.aconfig_cl import AConfigCl

app = Sanic("arcee")


etcd_host = os.environ.get('HX_ETCD_HOST')
etcd_port = int(os.environ.get('HX_ETCD_PORT'))
config_client = AConfigCl(host=etcd_host, port=etcd_port)


class ArceeState:
    STARTED = 1
    FINISHED = 2
    ERROR = 3
    ABORTED = 4


@app.on_request
async def add_start_time(request):
    request.ctx.start_time = time.time()


@app.on_response
async def add_spent_time(request, response):
    spend_time = round((time.time() - request.ctx.start_time) * 1000)
    logger.info("{} {} {} {} {}ms".format(response.status, request.method,
                                          request.path, request.query_string, spend_time))


def get_arcee_db_params() -> Tuple[str, str, str, str, str]:
    arcee_db_params = config_client.arcee_params()
    return asyncio.run(arcee_db_params)


async def get_cluster_secret() -> str:
    return await config_client.cluster_secret()


name, password, host, port, db_name = get_arcee_db_params()
uri = "mongodb://{u}:{p}@{host}:{port}/admin".format(
    u=name, p=password, host=host, port=port)
client = motor.motor_asyncio.AsyncIOMotorClient(uri)
db = client[db_name]


async def extract_token(request):
    # TODO: middleware
    token = request.headers.get('x-api-key')
    if not token:
        raise SanicException("API key is required", status_code=401)
    return token


async def check_token(token):
    token = await db.token.find_one({
        "$and": [
            {"deleted_at": 0},
            {"token": token},
        ]
    })
    if not token:
        raise SanicException("Token not found", status_code=401)


async def check_run_state(run):
    # state is finished or error
    if run['state'] in [2, 3]:
        raise SanicException("Run is completed", status_code=409)


async def extract_secret(request, raise_on):
    # TODO: middleware
    secret = request.headers.get('Secret')
    if not secret:
        if raise_on:
            raise SanicException("secret is required", status_code=401)
    return secret


async def check_secret(request, raise_on=True):
    secret = await extract_secret(request, raise_on)
    required = await get_cluster_secret()
    if raise_on:
        if secret != required:
            raise SanicException("secret is invalid", status_code=401)
    return secret == required


async def check_application(token, o):
    # check application
    p = await db.application.find_one({
        "_id": o["application_id"],
        "token": token,
        "deleted_at": 0
    })
    if not p:
        raise SanicException("given run not correspond to user", status_code=403)


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


async def check_goals(goals):
    """
    Checks goals
    :param goals:
    :return:
    """
    if goals is None:
        return
    if not isinstance(goals, list):
        raise SanicException("goals should be list", status_code=400)
    existing_goals = [doc["_id"] async for doc in db.goal.find({"_id": {"$in": goals}})]
    missing = list(filter(lambda x: x not in existing_goals, goals))
    if missing:
        msg = "some goals not exists in db: %s" % ",".join(missing)
        raise SanicException(msg, status_code=400)


@app.route('/arcee/v2/applications', methods=["POST", ])
async def create_application(request):
    token = await extract_token(request)
    await check_token(token)
    doc = request.json
    # TODO: validators
    key = doc.get("key")
    if not key or not isinstance(key, str):
        raise SanicException("Key should be str", status_code=400)
    goals = (doc.get("goals") or list())
    await check_goals(goals)
    display_name = doc.get("name", key)
    doc.update({"token": token})
    o = await db.application.find_one(
        {"token": token, "key": key, "deleted_at": 0})
    if o:
        raise SanicException("Project exists", status_code=409)
    doc["_id"] = str(uuid.uuid4())
    doc["name"] = display_name
    doc["deleted_at"] = 0
    await db.application.insert_one(doc)
    return json(doc)


@app.route('/arcee/v2/applications/<id_>', methods=["PATCH", ])
async def update_application(request, id_: str):
    """
    update application
    :param request:
    :param id_
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.application.find_one(
        {"token": token, "_id": id_, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    doc = request.json
    # TODO: validators
    goals = doc.get("goals")
    await check_goals(goals)
    display_name = doc.get("name")
    owner_id = doc.get('owner_id')
    d = {}
    if goals is not None:
        d.update({'goals': goals})
    if display_name is not None:
        d.update({'name': display_name})
    if owner_id is not None:
        d.update({'owner_id': owner_id})
    if d:
        await db.application.update_one(
            {"_id": id_}, {'$set': d})
    return json({"updated": bool(d), "id": id_})


@app.route('/arcee/v2/applications', methods=["GET", ])
async def get_applications(request):
    """
    Gets applications names based on provided token
    :param request:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    pipeline = [
        {"$match": {"token": token, "deleted_at": 0}},
        {
            "$lookup": {
                "from": "goal",
                "localField": "goals",
                "foreignField": "_id",
                "as": "applicationGoals"
            }
        },
    ]
    cur = db.application.aggregate(pipeline)
    return json([i async for i in cur])


@app.route('/arcee/v2/applications/bulk', methods=["GET", ])
async def bulk_get_applications(request):
    """
    Bulk get applications by application ids
    """
    token = await extract_token(request)
    await check_token(token)
    application_ids = request.args.getlist("application_id")
    if not application_ids:
        raise SanicException("application_id is required", status_code=400)
    match_filter = {
        "token": token,
        "_id": {"$in": application_ids},
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
                "from": "goal",
                "localField": "goals",
                "foreignField": "_id",
                "as": "applicationGoals"
            }
        },
    ]
    cur = db.application.aggregate(pipeline)
    return json([i async for i in cur])


@app.route('/arcee/v2/applications/<id_>', methods=["GET", ])
async def get_application(request, id_: str):
    """
    Gets applications names based on provided application id
    :param request:
    :param id_
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.application.find_one(
        {"token": token, "_id": id_, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    pipeline = [
        {"$match": {"token": token, "_id": id_}},
        {
            "$lookup": {
                "from": "goal",
                "localField": "goals",
                "foreignField": "_id",
                "as": "applicationGoals"
            }
        },
    ]
    cur = db.application.aggregate(pipeline)
    return json(await cur.next())


@app.route('/arcee/v2/applications/<id_>', methods=["DELETE", ])
async def delete_application(request, id_: str):
    """
    Deletes applications names based on provided application id
    :param request:
    :param id_
    :return:
    """
    deleted_logs = 0
    deleted_milestones = 0
    deleted_runs = 0
    deleted_stages = 0
    deleted_proc_data = 0
    token = await extract_token(request)
    await check_token(token)
    o = await db.application.find_one(
        {"token": token, "_id": id_, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    runs = [doc["_id"] async for doc in db.run.find({"application_id": id_})]
    if runs:
        results = await asyncio.gather(
            db.milestone.delete_many({'run_id': {'$in': runs}}),
            db.stage.delete_many({'run_id': {'$in': runs}}),
            db.proc_data.delete_many({'run_id': {'$in': runs}}),
            db.log.delete_many({'run': {'$in': runs}}),
            db.run.delete_many({"application_id": id_})
        )
        dm, ds, dpd, dl, dr = results
        deleted_milestones = dm.deleted_count
        deleted_stages = ds.deleted_count
        deleted_logs = dl.deleted_count
        deleted_runs = dr.deleted_count
        deleted_proc_data = dpd.deleted_count
    await db.application.update_one(
        {"_id": id_},
        {'$set': {"deleted_at": int(datetime.utcnow().timestamp())}})
    return json({
        "deleted": True,
        "_id": id_,
        "deleted_milestones": deleted_milestones,
        "deleted_logs": deleted_logs,
        "deleted_runs": deleted_runs,
        "deleted_stages": deleted_stages,
        "deleted_proc_data": deleted_proc_data
    })


@app.route('/arcee/v2/applications/<name>/run', methods=["POST", ])
async def create_application_run(request, name: str):
    """
    create application run
    :param request:
    :param name: str
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    # TODO: validators
    # find applications with given name-token
    o = await db.application.find_one(
        {"token": token, "key": name, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    application_id = o["_id"]
    doc = request.json
    imports = doc.get("imports", [])
    run_name = doc.get("name")
    run_cnt = await db.run.count_documents({"application_id": application_id})
    d = {
        "_id": str(uuid.uuid4()),
        "application_id": application_id,
        "start": int(datetime.utcnow().timestamp()),
        "finish": None,
        "state": ArceeState.STARTED,
        "name": run_name,
        "number": run_cnt + 1,
        "imports": imports,
        "deleted_at": 0,
    }
    await db.run.insert_one(
        d
    )
    return json({"id": d["_id"]})


async def reached_goals(run):

    result = dict()
    func_map = {
        'more': lambda x, y: x >= y,
        'less': lambda x, y: x <= y,
    }

    application_goals = run.get("application", {}).get("goals", [])
    data_goals = run.get("data", {})

    app_goals_all = [doc async for doc in db.goal.find({"_id": {"$in": application_goals}})]

    goals = {}
    for g in application_goals:
        filtered_goals = list(filter(lambda x: g == x["_id"], app_goals_all))
        if filtered_goals:
            gl = filtered_goals[0]
            goals[gl["key"]] = {
                "id": gl["_id"],
                "tendency": gl["tendency"],
                "target_value": gl["target_value"],
                "name": gl["name"],
            }

    for k, v in goals.items():
        # add application goal
        result[k] = dict()
        result[k].update(v)
        g = data_goals.get(k)
        if g:
            func = func_map.get(v.get("tendency"), lambda x, y: False)
            reached = func(g, v["target_value"])
            result[k]["value"] = g
            result[k]["reached"] = reached
        else:
            result[k]["reached"] = False
    return result


@app.route('/arcee/v2/run/<run_id>', methods=["GET", ])
async def get_run(request, run_id):
    """
    Gets application run by id
    :param request:
    :param run_id:
    :return:
    """
    token = None
    res = await check_secret(request, False)
    if not res:
        token = await extract_token(request)
        await check_token(token)
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    if token:
        # check project
        await check_application(token, o)
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
                "from": "application",
                "localField": "application_id",
                "foreignField": "_id",
                "as": "application"
            }
        },
        {
            "$unwind": '$application'
        }
    ]
    cur = db.run.aggregate(pipeline)
    run = await cur.next()
    reached = await reached_goals(run)
    run["reached_goals"] = reached
    return json(run)


@app.route('/arcee/v2/run/executors', methods=["GET", ])
async def get_executors(request):
    """
    Gets executors
    """
    token = await extract_token(request)
    await check_token(token)
    run_id = "run_id"
    application_id = "application_id"
    args = request.args
    supported_keys = [run_id, application_id]
    if len(args) != 1:
        raise SanicException("run_id / application_id is required", status_code=400)
    if not any(filter(lambda x: x in supported_keys, request.args.keys())):
        raise SanicException("run_id / application_id is supported", status_code=400)
    not_supported = list((filter(
        lambda x: x not in supported_keys, request.args.keys())))
    if not_supported:
        raise SanicException(
            "%s keys is not supported" % ','.join(not_supported), status_code=400)
    app_ids = []
    run_ids = []
    if application_id in request.args.keys():
        app_ids = request.args[application_id]
    if run_id in request.args.keys():
        run_ids = request.args[run_id]
    # ensure app ids provided for required token
    app_ids = [doc["_id"] async for doc in db.application.find(
        {
            "$and": [
                {"_id": {"$in": app_ids}},
                {"token": token},
                {"deleted_at": 0}
            ]}
    )]
    runs = [doc["_id"] async for doc in db.run.find(
        {
            "$or": [
                {"application_id": {"$in": app_ids}},
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


@app.route('/arcee/v2/run/<run_id>', methods=["PATCH", ])
async def update_run(request, run_id: str):
    """
    update application run
    :param request:
    :param run_id: str
    :return:
    """
    # firstly we try to use token (used for bulldozer)
    token = None
    res = await check_secret(request, False)
    if not res:
        token = await extract_token(request)
        await check_token(token)
    doc = request.json
    # TODO: validators
    finish = doc.get("finish", False)
    tags = doc.get("tags", {})
    hyperparameters = doc.get("hyperparameters", {})
    reason = doc.get("reason")
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Run not found", status_code=404)
    if token is not None:
        # omit check if accessed by secret
        await check_run_state(o)
        # check application
        await check_application(token, o)
    d = {}
    if finish:
        d.update({"finish": int(datetime.utcnow().timestamp())})
    if tags:
        d.update({"tags": tags})
    if hyperparameters:
        d.update({"hyperparameters": hyperparameters})
    if reason:
        d.update({"reason": reason})
    for param in ["state", "runset_id", "reason", "runset_name"]:
        value = doc.get(param)
        if value is not None:
            d.update({param: value})
    await db.run.update_one(
        {"_id": run_id}, {'$set': d})
    return json({"updated": True, "id": run_id})


@app.route('/arcee/v2/run/<run_id>/milestones', methods=["POST", ])
async def create_run_milestone(request, run_id: str):
    """
    create project run milestone
    :param request:
    :param run_id: str
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    doc = request.json
    milestone = doc.get("milestone")
    # TODO: validators
    # find project with given name-token
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_run_state(o)
    await check_application(token, o)
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


@app.route('/arcee/v2/run/<run_id>/milestones', methods=["GET", ])
async def get_milestones(request, run_id: str):
    """
    Get milestones for run
    :param request:
    :param run_id:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_application(token, o)
    res = [doc async for doc in db.milestone.find({"run_id": run_id})]
    return json(res)


@app.route('/arcee/v2/collect', methods=["POST", ])
async def collect(request):
    token = await extract_token(request)
    await check_token(token)
    r = json({'received': True, 'message': request.json})
    document = request.json
    platform = document.pop("platform", {})
    instance = platform.get("instance_id")
    run_id = document.get("run")
    if instance:
        o = await db.platform.find_one({"instance_id": instance})
        if not o and platform:
            platform["_id"] = str(uuid.uuid4())
            await db.platform.insert_one(platform)
        document["instance_id"] = instance
    document["_id"] = str(uuid.uuid4())
    document["time"] = datetime.utcnow().timestamp()
    run = await db.run.find_one({"_id": run_id})
    if not run:
        raise SanicException("Not found", status_code=404)
    await check_run_state(run)
    await db.log.insert_one(document)
    data = run.get("data", {})
    executors = run.get("executors", [])
    if instance:
        executors.append(instance)
    new_data = document.get("data", {})
    data.update(new_data)
    await db.run.update_one(
        {"_id": run_id}, {
            '$set': {
                "data": data,
                "executors": list(set(executors)),
            }
        })
    logger.info("x-api-key: %s, data: %s" % (request.headers['x-api-key'], request.json))
    return r


@app.route('/arcee/v2/applications/<app_id>/run', methods=["GET", ])
async def get_application_runs(request, app_id):
    """
    Gets application runs by application app_id
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.application.find_one(
        {"token": token, "_id": app_id, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    pipeline = [
        {"$match": {"application_id": app_id}},
        {
            "$lookup": {
                "from": "application",
                "localField": "application_id",
                "foreignField": "_id",
                "as": "application"
            }
        },
        {
            "$unwind": '$application'
        },
        {"$sort": {"start": -1}}
    ]
    cur = db.run.aggregate(pipeline)
    runs = [i async for i in cur]
    for run in runs:
        run["reached_goals"] = await reached_goals(run)
        run.pop("application", None)
    return json(runs)


@app.route('/arcee/v2/runs', methods=["GET", ])
async def get_runs(request):
    """
    List runs. runset_id is required when called with cluster secret
    """
    token = await extract_token(request)
    await check_token(token)

    runset_ids = request.args.getlist("runset_id")
    if runset_ids:
        match_q = {"$match": {"runset_id": {"$in": runset_ids}}}
    else:
        app_ids = await db.application.distinct(
            "_id", {"token": token, "deleted_at": 0})
        match_q = {"$match": {"application_id": {"$in": list(app_ids)}}}

    pipeline = [
        match_q,
        {
            "$lookup": {
                "from": "application",
                "localField": "application_id",
                "foreignField": "_id",
                "as": "application"
            }
        },
        {
            "$unwind": '$application'
        },
        {"$sort": {"start": -1}}
    ]
    cur = db.run.aggregate(pipeline)
    runs = [i async for i in cur]
    for run in runs:
        run["reached_goals"] = await reached_goals(run)
        run.pop("application", None)
    return json(runs)


@app.route('/arcee/v2/goals', methods=["POST", ])
async def create_goal(request):
    """
    create project goal
    :param request:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    # TODO: validators
    doc = request.json
    target_value = doc.get("target_value")
    tendency = doc.get("tendency")
    key = doc.get("key")
    name = doc.get("name")
    func = doc.get("func")
    if func:
        await check_func(func)
    # find project with given name-token
    o = await db.goal.find_one({"token": token, "key": key})
    if o:
        raise SanicException("Conflict", status_code=409)
    d = {
        "_id": str(uuid.uuid4()),
        "name": name,
        "tendency": tendency,
        "target_value": target_value,
        "key": key,
        "func": func,
        "token": token,
    }
    await db.goal.insert_one(
        d
    )
    return json(d)


@app.route('/arcee/v2/goals/', methods=["GET", ])
async def get_goals(request):
    """
    get goals
    :param request:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    res = [doc async for doc in db.goal.find({"token": token})]
    return json(res)


@app.route('/arcee/v2/goals/<goal_id>', methods=["GET", ])
async def get_goal(request, goal_id: str):
    """
    get goal
    :param request:
    :param goal_id:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.goal.find_one({"token": token, "_id": goal_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    return json(o)


@app.route('/arcee/v2/goals/<goal_id>', methods=["DELETE", ])
async def delete_goal(request, goal_id: str):
    """
    deletes goal
    :param request:
    :param goal_id:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.goal.find_one({"token": token, "_id": goal_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await db.goal.delete_one({'_id': goal_id})
    return json({"deleted": True, "_id": goal_id})


@app.route('/arcee/v2/run/<run_id>/logs', methods=["GET", ])
async def get_logs(request, run_id: str):
    """
    get logs for run
    :param request:
    :param run_id
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_application(token, o)
    res = [doc async for doc in db.log.find({"run": run_id})]
    return json(res)


@app.route('/arcee/v2/goals/<goal_id>', methods=["PATCH", ])
async def change_goal(request, goal_id: str):
    """
    update project goal
    :param request:
    :param goal_id:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    # TODO: validators
    doc = request.json
    target_value = doc.get("target_value")
    tendency = doc.get("tendency")
    display_name = doc.get("name")
    func = doc.get("func")
    o = await db.goal.find_one({"token": token, "_id": goal_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    d = {}
    if target_value is not None:
        d.update({'target_value': target_value})
    if tendency is not None:
        d.update({'tendency': tendency})
    if display_name is not None:
        d.update({'name': display_name})
    if func is not None:
        await check_func(func)
        d.update({'func': func})
    if d:
        await db.goal.update_one(
            {"_id": goal_id}, {'$set': d})
    return json({"updated": bool(d), "id": goal_id})


@app.route('/arcee/v2/applications/<app_id>/imports', methods=["GET", ])
async def get_imports(request, app_id: str):
    """
    Gets frameworks for application
    :param request:
    :param app_id:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.application.find_one(
        {"token": token, "_id": app_id, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    pipeline = [
        {"$match": {"application_id": app_id}},
        {
            "$group": {
                "_id": app_id,
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
        r = {"_id": app_id, "key": name, "imports": list()}
    return json(r)


@app.route('/arcee/v2/tokens', methods=["POST", ])
async def create_token(request):
    """
    creates token
    :param request:
    :return:
    """
    await check_secret(request)
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


@app.route('/arcee/v2/tokens/<token>', methods=["DELETE", ])
async def delete_token(request, token: str):
    """
    deletes token
    :param request:
    :param token:
    :return:
    """
    await check_secret(request)
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


@app.route('/arcee/v2/tokens/<token>', methods=["GET", ])
async def get_token(request, token: str):
    """
    get token
    :param request:
    :param token:
    :return:
    """
    await check_secret(request)
    token = await db.token.find_one({
        "$and": [
            {"deleted_at": 0},
            {
                "$or": [
                    {"token": token},
                    {"_id":  token}
                ]
            }
        ]
    })
    if not token:
        raise SanicException("Not found", status_code=404)
    return json(token)


@app.route('/arcee/v2/run/<run_id>/stages', methods=["POST", ])
async def create_stage(request, run_id: str):
    """
    create project run stage
    :param request:
    :param run_id: str
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    doc = request.json
    stage_name = doc.get("stage")
    if not stage_name:
        raise SanicException("stage name is required", status_code=400)
    # find project with given name-token
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_run_state(o)
    await check_application(token, o)
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


@app.route('/arcee/v2/run/<run_id>/stages', methods=["GET", ])
async def get_stages(request, run_id: str):
    """
    Get stages
    :param request:
    :param run_id:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_application(token, o)
    res = [doc async for doc in db.stage.find({"run_id": run_id})]
    return json(res)


@app.route('/arcee/v2/run/<run_id>/proc', methods=["POST", ])
async def create_proc_data(request, run_id: str):
    """
    create proc data log
    :param request:
    :param run_id: str
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    doc = request.json
    # TODO: validators
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_application(token, o)
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


@app.route('/arcee/v2/run/<run_id>/proc', methods=["GET", ])
async def get_proc_data(request, run_id: str):
    """
    Get proc data for run
    :param request:
    :param run_id:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.run.find_one({"_id": run_id})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_application(token, o)
    res = [doc async for doc in db.proc_data.find({"run_id": run_id})]
    return json(res)


@app.route('/arcee/v2/executors/<executor_id>/runs', methods=["GET", ])
async def get_run_ids_by_executor(request, executor_id: str):
    """
     Gets Run Ids by executor id
    :param request:
    :param executor_id: str
    :return:
    """
    await check_secret(request)
    application_id = "application_id"
    app_ids = list()
    supported_keys = [application_id]
    not_supported = list((filter(
        lambda x: x not in supported_keys, request.args.keys())))
    if not_supported:
        raise SanicException(
            "%s keys are not supported" % ','.join(not_supported), status_code=400)
    if application_id in request.args.keys():
        app_ids = request.args[application_id]
    run_ids = await db.proc_data.distinct("run_id", {"instance_id": executor_id})
    if app_ids:
        app_run_ids = [doc["_id"] async for doc in db.run.find({"application_id": {"$in": app_ids}})]
        run_ids = list(set(run_ids) & set(app_run_ids))
    return json(run_ids)


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
            'mongo_database': db_name
        }
        manager = MigrationManager(config=Configuration(config=config_params))
        manager.run()
    logger.info('Starting server')
    app.run(host='0.0.0.0', port=8891, access_log=False)
