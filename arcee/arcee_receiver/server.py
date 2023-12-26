import time
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone
import asyncio
from enum import Enum

from etcd import Lock as EtcdLock, Client as EtcdClient
from typing import Tuple, Optional, List, Union
import os
import uuid

from mongodb_migrations.cli import MigrationManager
from mongodb_migrations.config import Configuration
from sanic import Sanic
from sanic.log import logger
from sanic.response import json
from sanic.exceptions import SanicException
import motor.motor_asyncio
from sanic_ext import validate
from typing_extensions import Annotated

from arcee_receiver.modules.leader_board import (
    get_calculated_leaderboard, Tendencies)
from arcee_receiver.modules.leader_board import get_goals as _get_app_goals

from optscale_client.aconfig_cl.aconfig_cl import AConfigCl

from pydantic import BaseModel, Field, BeforeValidator

app = Sanic("arcee")

etcd_host = os.environ.get('HX_ETCD_HOST')
etcd_port = int(os.environ.get('HX_ETCD_PORT'))
config_client = AConfigCl(host=etcd_host, port=etcd_port)

DAY_IN_SEC = 86400


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


class SubDataset(BaseModel):
    path: str
    timespan_from: Optional[int] = None
    timespan_to: Optional[int] = None


class DatasetPatchIn(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    labels: List[str] = []
    training_set: Optional[SubDataset] = None
    validation_set: Optional[SubDataset] = None


class DatasetPostIn(DatasetPatchIn):
    path: str


class Dataset(DatasetPostIn):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='_id')
    token: str
    created_at: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp()))
    deleted_at: int = 0


class RunPatchIn(BaseModel):
    finish: Optional[bool] = None
    tags: Optional[dict] = {}
    hyperparameters: Optional[dict] = {}
    reason: Optional[str] = None
    state: Optional[int] = None
    runset_id: Optional[str] = None
    runset_name: Optional[str] = None


class Git(BaseModel):
    remote: str
    branch: str
    commit_id: str
    status: str


class RunPostIn(BaseModel):
    name: str
    imports: list[str] = []
    git: Optional[Git] = None
    command: str


class Run(RunPostIn, RunPatchIn):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='_id')
    application_id: str
    start: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp()))
    number: int
    deleted_at: int = 0
    data: dict = {}
    executors: list = []
    dataset_id: Optional[str] = None
    state: int = ArceeState.STARTED
    finish: Optional[int] = None


class ApplicationPatchIn(BaseModel):
    goals: Optional[List[str]] = []
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None


class ConsolePostIn(BaseModel):
    output: str
    error: str


class Console(ConsolePostIn):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='_id')
    run_id: str


class LeaderboardDatasetPatchIn(BaseModel):
    dataset_ids: Optional[list]
    name: Optional[str]

    @staticmethod
    def remove_dup_ds_ids(kwargs):
        ds_ids = kwargs.get("dataset_ids")
        if ds_ids:
            kwargs["dataset_ids"] = list(set(ds_ids))


class LeaderboardDatasetPostIn(LeaderboardDatasetPatchIn):
    name: str


class LeaderboardDataset(LeaderboardDatasetPostIn):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='_id')
    token: str
    leaderboard_id: str
    created_at: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp()))
    deleted_at: int = 0


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
    # TODO: middleware?
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
    if not isinstance(goals, list):
        raise SanicException("goals should be list", status_code=400)
    if not goals:
        return
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
    description = doc.get("description")
    doc.update({"token": token})
    o = await db.application.find_one(
        {"token": token, "key": key, "deleted_at": 0})
    if o:
        raise SanicException("Project exists", status_code=409)
    doc["_id"] = str(uuid.uuid4())
    doc["name"] = display_name
    doc["deleted_at"] = 0
    doc["description"] = description
    await db.application.insert_one(doc)
    return json(doc)


@app.route('/arcee/v2/applications/<id_>', methods=["PATCH", ])
@validate(json=ApplicationPatchIn)
async def update_application(request, body: ApplicationPatchIn, id_: str):
    """
    update application
    :param request:
    :param body:
    :param id_:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.application.find_one(
        {"token": token, "_id": id_, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)
    await check_goals(body.goals)
    goals_to_remove = set(o['goals']) - set(body.goals)
    for goal_id in goals_to_remove:
        if await _goal_used_in_lb(db, goal_id, application_id=id_):
            raise SanicException(f"Goal is used in application leaderboard(s)",
                                 status_code=409)
    d = body.model_dump(exclude_unset=True)
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
    :param id_:
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
    :param id_:
    :return:
    """
    deleted_logs = 0
    deleted_milestones = 0
    deleted_runs = 0
    deleted_stages = 0
    deleted_proc_data = 0
    deleted_consoles = 0
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
            db.run.delete_many({"application_id": id_}),
            db.console.delete_many({'run_id': {'$in': runs}})
        )
        dm, ds, dpd, dl, dr, dc = results
        deleted_milestones = dm.deleted_count
        deleted_stages = ds.deleted_count
        deleted_logs = dl.deleted_count
        deleted_runs = dr.deleted_count
        deleted_proc_data = dpd.deleted_count
        deleted_consoles = dc.deleted_count
    leaderboard = await db.leaderboard.find_one(
        {"token": token, "application_id": id_, "deleted_at": 0})
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
        "deleted_proc_data": deleted_proc_data,
        "deleted_console_output": deleted_consoles
    })


@app.route('/arcee/v2/applications/<name>/run', methods=["POST", ])
@validate(json=RunPostIn)
async def create_application_run(request, body: RunPostIn, name: str):
    """
    create application run
    :param body:
    :param request:
    :param name: str
    :return:
    """
    token = await extract_token(request)
    await check_token(token)

    o = await db.application.find_one(
        {"token": token, "key": name, "deleted_at": 0})
    if not o:
        raise SanicException("Not found", status_code=404)

    application_id = o["_id"]
    run_cnt = await db.run.count_documents({"application_id": application_id})
    r = Run(
        application_id=application_id, number=run_cnt + 1, **body.model_dump()
    )

    await db.run.insert_one(r.model_dump(by_alias=True))
    return json({"id": r.id})


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
        if g is not None:
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
@validate(json=RunPatchIn)
async def update_run(request, body: RunPatchIn, run_id: str):
    """
    update application run
    :param body:
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

    r = await db.run.find_one({"_id": run_id})
    if not r:
        raise SanicException("Run not found", status_code=404)
    if token is not None:
        # omit check if accessed by secret
        await check_run_state(r)
        # check application
        await check_application(token, r)

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


class PlatformType(str, Enum):
    ali = "ali"
    aws = "aws"
    azure = "azure"
    gcp = "gcp"
    unknown = "unknown"


class InstanceLifeCycle(str, Enum):
    OnDemand = "OnDemand"
    Preemptible = "Preemptible"
    Spot = "Spot"
    Unknown = "Unknown"


class PlatformPostIn(BaseModel):
    platform_type: PlatformType
    instance_id: str
    account_id: str
    local_ip: str
    public_ip: str
    instance_lc: InstanceLifeCycle
    instance_type: str
    instance_region: str
    availability_zone: str


def filter_strings(stats: dict) -> dict:
    return {k: v for k, v in stats.items() if isinstance(v, (int, float))}


StatsData = Annotated[
    dict[str, Union[int, float]], BeforeValidator(filter_strings)]


class StatsPostIn(BaseModel):
    project: str
    run: str
    data: StatsData
    platform: PlatformPostIn


class Platform(PlatformPostIn):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='_id')


class Log(BaseModel):
    project: str
    run: str
    data: StatsData
    instance_id: Optional[str]
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='_id')
    time: float = Field(
        default_factory=lambda: datetime.utcnow().timestamp())


@app.route('/arcee/v2/collect', methods=["POST", ])
@validate(json=StatsPostIn)
async def collect(request, body: StatsPostIn):
    token = await extract_token(request)
    await check_token(token)

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
              run=body.run, data=body.data)
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


@app.route('/arcee/v2/applications/<application_id>/runs/bulk', methods=["GET", ])
async def bulk_get_runs(request, application_id: str):
    """
    Bulk get runs by run ids
    """
    token = await extract_token(request)
    await check_token(token)
    run_ids = request.args.getlist("run_id")
    if not run_ids:
        raise SanicException("run_ids is required", status_code=400)
    o = await db.application.find_one(
        {"token": token, "_id": application_id, "deleted_at": 0})
    if not o:
        raise SanicException("Application not found", status_code=404)
    goals = await _get_app_goals(db, application_id)
    pipeline = [
        {
            "$match": {
                "_id": {
                    "$in": run_ids
                },
                "application_id": application_id
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
                "application_id": 1,
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
            gl = goals.get(k, {})
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


async def _goal_used_in_lb(db, goal_id: str, application_id: str=None):
    match_block = [
        {"deleted_at": {"$eq": 0}},
        {
            "$expr": {
                "$or": [
                    {"$eq": ["$primary_goal", "$$goalId"]},
                    {"$in": ["$$goalId", {"$ifNull": ["$other_goals", []]}]}
                ]
            }
        }]
    if application_id:
        match_block.append({'application_id': application_id})
    pipeline = [
        {
            "$match": {
                "_id": goal_id
            }
        },
        {
            "$lookup": {
                "from": "leaderboard",
                "let": {"goalId": "$_id"},
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
                "as": "used_in_leaderboard"
            }
        },
        {
            "$project": {
                "goal_used": {"$gt": [{"$size": "$used_in_leaderboard"}, 0]}
            }
        }
    ]
    cur = db.goal.aggregate(pipeline)
    try:
        ri = await cur.next()
    except StopAsyncIteration:
        return False
    return ri.get("goal_used", False)


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
    if await _goal_used_in_lb(db, goal_id):
        raise SanicException("Goal used in leaderboard", status_code=409)
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
                    {"_id": token}
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


@app.route('/arcee/v2/executors/breakdown', methods=["GET", ])
async def get_executors_breakdown(request):
    token = await extract_token(request)
    await check_token(token)

    application_ids = await db.application.distinct(
        "_id", {"token": token, "deleted_at": 0})
    if not application_ids:
        return json({})

    pipeline = [
        {"$match": {"application_id": {"$in": application_ids}}},
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


@app.route('/arcee/v2/applications/<application_id>/leaderboards',
           methods=["POST", ])
async def create_leaderboard(request, application_id: str):
    """
    create leaderboard
    :param request:
    :param application_id: str
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    # TODO: validators
    doc = request.json
    primary_goal = doc.get('primary_goal')
    other_goals = doc.get('other_goals', [])
    filters = doc.get("filters", [])
    grouping_tags = doc.get('grouping_tags', [])
    group_by_hp = doc.get('group_by_hp', False)
    # find leaderboard with given application_id
    exists = await db.leaderboard.find_one(
        {"token": token, "application_id": application_id, "deleted_at": 0})
    if exists:
        raise SanicException("Conflict", status_code=409)
    leaderboard = {
        "_id": str(uuid.uuid4()),
        "application_id": application_id,
        "grouping_tags": grouping_tags,
        "primary_goal": primary_goal,
        "other_goals": other_goals,
        "filters": filters,
        "group_by_hp": group_by_hp,
        "token": token,
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp())
    }
    await db.leaderboard.insert_one(leaderboard)
    return json(leaderboard)


async def _create_leaderboard_dataset(**kwargs) -> dict:
    LeaderboardDataset.remove_dup_ds_ids(kwargs)
    d = LeaderboardDataset(**kwargs).model_dump(by_alias=True)
    await db.leaderboard_dataset.insert_one(d)
    return d


@app.route('/arcee/v2/leaderboards/<leaderboard_id>/leaderboard_datasets',
           methods=["POST", ])
@validate(json=LeaderboardDatasetPostIn)
async def create_leaderboard_dataset(request, body: LeaderboardDatasetPostIn, leaderboard_id: str):
    token = await extract_token(request)
    await check_token(token)

    leaderboard = await db.leaderboard.find_one(
        {"token": token, "_id": leaderboard_id, "deleted_at": 0})
    if not leaderboard:
        raise SanicException("Leaderboard not found", status_code=404)
    d = await _create_leaderboard_dataset(token=token, leaderboard_id=leaderboard_id,
                                          **body.model_dump())
    return json(d, status=201)


@app.route('/arcee/v2/leaderboard_datasets/<id_>', methods=["GET", ])
async def get_leaderboard_dataset(request, id_: str):
    token = await extract_token(request)
    await check_token(token)
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


@app.route('/arcee/v2/leaderboards/<leaderboard_id>/leaderboard_datasets', methods=["GET", ])
async def get_leaderboard_datasets(request, leaderboard_id: str):
    token = await extract_token(request)
    await check_token(token)
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
                "from": "leaderboard",
                "localField": "leaderboard_id",
                "foreignField": "_id",
                "as": "leaderboard"
            }
        },
        {
            "$unwind": "$leaderboard"
        },
        {
            "$lookup": {
                "from": "goal",
                "localField": "leaderboard.primary_goal",
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
                    tendency == Tendencies.MORE.value and best_score < cand_score) or (
                    tendency == Tendencies.LESS.value and best_score > cand_score)):
                best_score = cand_score
        leaderboard_dataset['primary_metric']['value'] = best_score
        result.append(leaderboard_dataset)
    return json(result)


@app.route('/arcee/v2/leaderboard_datasets/<id_>', methods=["PATCH", ])
@validate(json=LeaderboardDatasetPatchIn)
async def update_leaderboard_dataset(request, body: LeaderboardDatasetPatchIn, id_: str):
    token = await extract_token(request)
    await check_token(token)
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
        LeaderboardDatasetPatchIn.remove_dup_ds_ids(d)
        await db.leaderboard_dataset.update_one(
            {"_id": id_}, {'$set': d})
    o = await db.leaderboard_dataset.find_one({"_id": id_})
    return json(o)


@app.route('/arcee/v2/leaderboard_datasets/<id_>', methods=["DELETE", ])
async def delete_leaderboard_dataset(request, id_: str):
    token = await extract_token(request)
    await check_token(token)
    o = await db.leaderboard_dataset.find_one({"token": token, "_id": id_})
    if not o:
        raise SanicException("LeaderboardDataset not found", status_code=404)
    await db.leaderboard_dataset.update_one({"_id": id_}, {'$set': {
        "deleted_at": int(datetime.utcnow().timestamp())
    }})
    return json('', status=204)


@app.route('/arcee/v2/leaderboard_datasets/<id_>/details', methods=["GET", ])
async def get_leaderboard_dataset_details(request, id_: str):
    token = await extract_token(request)
    await check_token(token)
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


@app.route('/arcee/v2/applications/<application_id>/leaderboards',
           methods=["GET", ])
async def get_leaderboard(request, application_id: str):
    """
    get leaderboard
    :param request:
    :param application_id: str
    :return:
    """
    response = {}
    token = await extract_token(request)
    await check_token(token)
    leaderboard = await db.leaderboard.find_one(
        {"token": token, "application_id": application_id, "deleted_at": 0})
    if leaderboard:
        response = leaderboard
    return json(response)


@app.route('/arcee/v2/applications/<application_id>/leaderboards',
           methods=["PATCH", ])
async def change_leaderboard(request, application_id: str):
    """
    update leaderboard
    :param request:
    :param application_id: str
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    # TODO: validators
    doc = request.json
    leaderboard = await db.leaderboard.find_one(
        {"token": token, "application_id": application_id, "deleted_at": 0})
    if not leaderboard:
        raise SanicException("Not found", status_code=404)

    for key, param in {
        'primary_goal': doc.get('primary_goal'),
        'grouping_tags': doc.get('grouping_tags'),
        'other_goals': doc.get('other_goals'),
        'filters': doc.get("filters"),
        'group_by_hp': doc.get('group_by_hp')
    }.items():
        if param is not None:
            leaderboard.update({
                key: param
            })
    if leaderboard:
        await db.leaderboard.update_one(
            {"_id": leaderboard['_id']}, {'$set': leaderboard})
    return json({"updated": bool(leaderboard), "id": leaderboard['_id']})


@app.route('/arcee/v2/applications/<application_id>/leaderboards',
           methods=["DELETE", ])
async def delete_leaderboard(request, application_id: str):
    """
    deletes leaderboard
    :param request:
    :param application_id: str
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    leaderboard = await db.leaderboard.find_one(
        {"token": token, "application_id": application_id, "deleted_at": 0})
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
           methods=["GET", ])
async def leaderboard_details(request, leaderboard_dataset_id: str):
    """
    Calculate leaderboard
    :param request:
    :param leaderboard_dataset_id: str
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    lb = await get_calculated_leaderboard(db, token, leaderboard_dataset_id)
    return json(lb)


async def _create_dataset(**kwargs) -> dict:
    d = Dataset(**kwargs).model_dump(by_alias=True)
    await db.dataset.insert_one(d)
    return d


@app.route('/arcee/v2/datasets', methods=["POST", ])
@validate(json=DatasetPostIn)
async def create_dataset(request, body: DatasetPostIn):
    token = await extract_token(request)
    await check_token(token)
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


@app.route("/arcee/v2/run/<run_id>/dataset_register", methods=["POST", ])
@validate(json=DatasetPostIn)
async def register_dataset(request, body: DatasetPostIn, run_id: str):
    token = await extract_token(request)
    await check_token(token)
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


@app.route('/arcee/v2/datasets', methods=["GET", ])
async def get_datasets(request):
    token = await extract_token(request)
    await check_token(token)
    match_filter = {
        "token": token,
        "deleted_at": 0
    }
    # TODO: possibly move to bulk_get API with ability to get deleted objects
    include_deleted = "include_deleted"
    if (include_deleted in request.args.keys() and
            await to_bool(request.args.get(include_deleted))):
        match_filter.pop('deleted_at')
    res = [Dataset(**doc).model_dump(by_alias=True)
           async for doc in db.dataset.find(match_filter)]
    return json(res)


@app.route('/arcee/v2/datasets/<id_>', methods=["GET", ])
async def get_dataset(request, id_: str):
    token = await extract_token(request)
    await check_token(token)
    d = await db.dataset.find_one(
        {"$and": [
            {"token": token},
            {"_id": id_},
            {"deleted_at": 0}
        ]})
    if not d:
        raise SanicException("Dataset not found", status_code=404)
    return json(Dataset(**d).model_dump(by_alias=True))


@app.route('/arcee/v2/datasets/<id_>', methods=["PATCH", ])
@validate(json=DatasetPatchIn)
async def update_dataset(request, body: DatasetPatchIn, id_: str):
    token = await extract_token(request)
    await check_token(token)
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


async def _dataset_used_in_leaderboard(db, dataset_id: str):
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
    cur = db.dataset.aggregate(pipeline)
    try:
        ri = await cur.next()
    except StopAsyncIteration:
        return False
    return ri.get("used", False)


@app.route('/arcee/v2/datasets/<id_>', methods=["DELETE", ])
async def delete_dataset(request, id_: str):
    token = await extract_token(request)
    await check_token(token)
    o = await db.dataset.find_one({"token": token, "_id": id_})
    if not o:
        raise SanicException("Dataset not found", status_code=404)
    if await _dataset_used_in_leaderboard(db, id_):
        raise SanicException("Dataset used in leaderboard", status_code=409)
    await db.dataset.update_one({"_id": id_}, {'$set': {
        "deleted_at": int(datetime.utcnow().timestamp())
    }})
    return json('', status=204)


@app.route('/arcee/v2/labels', methods=["GET", ])
async def get_labels(request):
    token = await extract_token(request)
    await check_token(token)
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


@app.route('/arcee/v2/run/<run_id>/consoles', methods=["POST", ])
@validate(json=ConsolePostIn)
async def create_run_console(request, body: ConsolePostIn, run_id: str):
    token = await extract_token(request)
    await check_token(token)
    run = await db.run.find_one({"_id": run_id})
    if not run:
        raise SanicException("Not found", status_code=404)
    await check_run_state(run)
    await check_application(token, run)
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


@app.route('/arcee/v2/run/<run_id>/console', methods=["GET", ])
async def get_run_console(request, run_id: str):
    token = await extract_token(request)
    await check_token(token)
    console = await db.console.find_one(
        {"run_id": run_id})
    if not console:
        raise SanicException("Not found", status_code=404)
    return json(console)


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
