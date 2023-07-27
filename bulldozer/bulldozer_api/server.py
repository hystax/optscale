import datetime
import asyncio
from typing import Tuple
import os
import uuid
from sanic import Sanic
from sanic.response import json
from sanic.log import logger
from sanic.exceptions import SanicException
import motor.motor_asyncio


from cost_calc import CostCalc
from producer import TaskProducer
from name_generator import NameGenerator
from utils import permutation

from aconfig_cl.aconfig_cl import AConfigCl


app = Sanic("bulldozer")


etcd_host = os.environ.get('HX_ETCD_HOST')
etcd_port = int(os.environ.get('HX_ETCD_PORT'))
config_client = AConfigCl(host=etcd_host, port=etcd_port)


class TaskState:

    STARTING_PREPARING = 1
    STARTING = 2
    STARTED = 3
    DESTROYING_SCHEDULED = 4
    DESTROY_PREPARING = 5
    DESTROYING = 6
    DESTROYED = 7
    ERROR = 9
    WAITING_ARCEE = 10


class RunsetState:

    CREATED = 1
    RUNNING = 2
    STOPPING = 3
    ERROR = 4
    STARTED = 5
    STOPPED = 6


# runner number is limited
MAX_RUNNER_NUM = 15


def get_db_params() -> Tuple[str, str, str, str, str]:
    db_params = config_client.bulldozer_params()
    return asyncio.run(db_params)


async def get_cluster_secret() -> str:
    return await config_client.cluster_secret()


name, password, host, port, db = get_db_params()
uri = "mongodb://{u}:{p}@{host}:{port}/admin".format(
    u=name, p=password, host=host, port=port)
client = motor.motor_asyncio.AsyncIOMotorClient(uri)
db = client[db]

cost_calc = CostCalc()


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


@app.route('/bulldozer/v2/tokens/<token>', methods=["GET", ])
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
        raise SanicException("Token not found", status_code=404)
    return json(token)


@app.route('/bulldozer/v2/tokens', methods=["POST", ])
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
        "created": int(datetime.datetime.utcnow().timestamp()),
        "deleted_at": 0,
    }
    await db.token.insert_one(
        d
    )
    return json(d)


@app.route('/bulldozer/v2/tokens/<token>', methods=["DELETE", ])
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
        raise SanicException("Token not found", status_code=404)
    token_id = token["_id"]
    await db.token.update_one(
        {"_id": token_id}, {
            '$set': {
                "deleted_at": int(
                    datetime.datetime.utcnow().timestamp()),
            }
        })
    return json(
        '',
        status=204
    )


@app.route('/bulldozer/v2/templates', methods=["POST", ])
async def create_template(request):
    token = await extract_token(request)
    await check_token(token)
    doc = request.json
    # TODO: validators
    name = doc.get("name")
    if not name or not isinstance(name, str):
        raise SanicException("Name required and should be string", status_code=400)
    o = await db.template.find_one(
        {"$and": [
            {"token": token},
            {"name": name},
            {"deleted_at": 0}
        ]})
    if o:
        raise SanicException(
            "Template with %s exists" % name, status_code=409)
    application_ids = (doc.get("application_ids") or list())
    cloud_account_ids = (doc.get("cloud_account_ids") or list())

    if len(application_ids) < 1:
        raise SanicException("At least 1 application is required",
                             status_code=400)
    region_ids = (doc.get("region_ids") or list())
    if len(region_ids) < 1:
        raise SanicException("At least 1 region is required",
                             status_code=400)
    instance_types = (doc.get("instance_types") or list())
    if len(instance_types) < 1:
        raise SanicException("At least 1 instance type is required",
                             status_code=400)
    # TODO: raise if not set?
    budget = (doc.get("budget") or 0.00)
    name_prefix = doc.get("name_prefix")
    if not name_prefix:
        raise SanicException("name_prefix is required",
                             status_code=400)
    tags = (doc.get("tags") or dict())
    hyperparameters = doc.get("hyperparameters")
    d = {
        "_id": str(uuid.uuid4()),
        "name": name,
        "application_ids": application_ids,
        "cloud_account_ids": cloud_account_ids,
        "region_ids": region_ids,
        "instance_types": instance_types,
        "budget": budget,
        "name_prefix": name_prefix,
        "token": token,
        "tags": tags,
        "hyperparameters": hyperparameters,
        "created_at": int(datetime.datetime.utcnow().timestamp()),
        "deleted_at": 0
    }
    await db.template.insert_one(d)
    return json(d, status=201)


@app.route('/bulldozer/v2/templates/', methods=["GET", ])
async def get_templates(request):
    """
    get templates
    :param request:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    # TODO: exclude deleted
    res = [doc async for doc in db.template.find(
        {"$and": [
            {"token": token},
            {"deleted_at": 0}
        ]})]
    return json(res)


@app.route('/bulldozer/v2/templates/<id_>', methods=["GET", ])
async def get_template(request, id_: str):
    """
    gets template
    :param request:
    :param id_
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.template.find_one(
        {"$and": [
            {"token": token},
            {"_id": id_},
            {"deleted_at": 0}
        ]})
    if not o:
        raise SanicException("Template not found", status_code=404)
    return json(o)


@app.route('/bulldozer/v2/templates/<id_>', methods=["PATCH", ])
async def update_template(request, id_: str):
    """
    update template
    :param request:
    :param id_
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    o = await db.template.find_one(
        {"$and": [
            {"token": token},
            {"_id": id_},
            {"deleted_at": 0}
        ]})
    if not o:
        raise SanicException("Template not found", status_code=404)
    doc = request.json
    # TODO: validators
    d = dict()
    name = doc.get("name")
    if name is not None:
        if not isinstance(name, str):
            raise SanicException("Name required and should be string", status_code=400)
        # TODO: exclude deleted
        if name != o["name"]:
            o = await db.template.find_one(
                {"$and": [
                    {"token": token},
                    {"name": name},
                    {"deleted_at": 0}
                ]})
            if o:
                raise SanicException(
                    "Template with %s exists" % name, status_code=409)
        d.update({"name": name})

    application_ids = doc.get("application_ids")
    if application_ids is not None:
        if len(application_ids) < 1:
            raise SanicException("At least 1 application is required",
                                 status_code=400)
        d.update({"application_ids": application_ids})

    region_ids = doc.get("region_ids")
    if region_ids is not None:
        if len(region_ids) < 1:
            raise SanicException("At least 1 region is required",
                                 status_code=400)
        d.update({"region_ids": region_ids})

    instance_types = doc.get("instance_types")
    if instance_types is not None:
        if len(instance_types) < 1:
            raise SanicException("At least 1 instance type is required",
                                 status_code=400)
        d.update({"instance_types": instance_types})

    budget = doc.get("budget")
    if budget is not None:
        d.update({"budget": budget})

    name_prefix = doc.get("name_prefix")
    if name_prefix is not None:
        d.update({"name_prefix": name_prefix})

    cloud_account_ids = doc.get("cloud_account_ids")
    if cloud_account_ids is not None:
        d.update({"cloud_account_ids": cloud_account_ids})

    tags = doc.get("tags")
    if tags is not None:
        d.update({"tags": tags})

    hp = doc.get("hyperparameters")
    if hp is not None:
        d.update({"hyperparameters": hp})
    if d:
        await db.template.update_one(
            {"_id": id_}, {'$set': d})
    o = await db.template.find_one({"_id": id_})
    return json(o)


@app.route('/bulldozer/v2/templates/<id_>', methods=["DELETE", ])
async def delete_template(request, id_: str):
    """
    Deletes template
    :param request:
    :param id_
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    # TODO: deleted?
    o = await db.template.find_one({"token": token, "_id": id_})
    if not o:
        raise SanicException("Template not found", status_code=404)
    # check for create runsets
    runset_ids = [doc["_id"] async for doc in db.runset.find({"template_id": id_})]
    if runset_ids:
        raise SanicException("Template has runsets: %s" % (
            ",".join(runset_ids)
        ), status_code=409)

    await db.template.update_one({"_id": id_}, {'$set': {
        "deleted_at": int(datetime.datetime.utcnow().timestamp())
    }})
    return json(
        '',
        status=204
    )


async def _create_runner(
        runset_id: str,
        cloud_account_id: str,
        hyperparameters: dict,
        region_id: str,
        instance_type: str,
        name_prefix: str,
        application_id: str,
        tags: dict,
        destroy_conditions: dict,
        commands: str,
        token: str,
        created_at: int,
        spot_settings: dict,
        open_ingress: bool,
):
    runner = {
        "_id": str(uuid.uuid4()),
        "runset_id": runset_id,
        "state": TaskState.STARTING_PREPARING,
        "cloud_account_id": cloud_account_id,
        "hyperparameters": hyperparameters,
        "region_id": region_id,
        "instance_type": instance_type,
        "name_prefix": name_prefix,
        "application_id": application_id,
        "tags": tags,
        "destroy_conditions": destroy_conditions,
        "commands": commands,
        "token": token,
        "created_at": created_at,
        "destroyed_at": 0,
        "started_at": 0,
        "name": "",
        "spot_settings": spot_settings,
        "open_ingress": open_ingress,
    }
    await db.runner.insert_one(runner)
    return runner["_id"]


async def submit_tasks(runners, state):

    producer = TaskProducer()
    for runner in runners:
        task = {
            "state": state,
            "runner_id": runner,
            "try": 0,
            "updated": int(datetime.datetime.utcnow().timestamp()),
            "reason": "",
            "infra_try": 0
        }
        logger.info("submitting task for runner:%s, state:%d", runner, state)
        await TaskProducer.run_async(producer.create_task, task)


@app.route('/bulldozer/v2/templates/<template_id>/runsets', methods=["POST", ])
async def create_runset(request, template_id: str):
    """
    Creates runset
    :param request:
    :param template_id:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    doc = request.json
    # TODO: validators
    o = await db.template.find_one(
        {"$and": [
            {"token": token},
            {"_id": template_id},
            {"deleted_at": 0}
        ]})
    if not o:
        raise SanicException(
            "Template not exists", status_code=404)
    # TODO: strict check args!
    application_id = doc.get("application_id")
    cloud_account_id = doc.get("cloud_account_id")
    region_id = doc.get("region_id")
    instance_type = doc.get("instance_type")
    name_prefix = doc.get("name_prefix")
    tags = doc.get("tags")
    hyperparameters = doc.get("hyperparameters")
    destroy_conditions = doc.get("destroy_conditions")
    owner_id = doc.get("owner_id")
    commands = doc.get("commands")
    spot_settings = doc.get("spot_settings")
    open_ingress = doc.get("open_ingress", False)
    runset_id = str(uuid.uuid4())
    runset_cnt = await db.runset.count_documents({"template_id": template_id})
    created_at = int(datetime.datetime.utcnow().timestamp())
    d = {
        "_id": runset_id,
        "name": NameGenerator.get_random_name(),
        "number": runset_cnt + 1,
        "template_id": template_id,
        "application_id": application_id,
        "cloud_account_id": cloud_account_id,
        "region_id": region_id,
        "instance_type": instance_type,
        "name_prefix": name_prefix,
        "tags": tags,
        "hyperparameters": hyperparameters,
        "destroy_conditions": destroy_conditions,
        "owner_id": owner_id,
        "commands": commands,
        "token": token,
        "state": RunsetState.CREATED,
        "created_at": created_at,
        "started_at": 0,
        "destroyed_at": 0,
        "deleted_at": 0,
        "spot_settings": spot_settings,
        "open_ingress": open_ingress,
    }
    # TODO: create runners
    runners_hp = permutation(hyperparameters)
    runners = list()
    for num, i in enumerate(runners_hp):
        if num == MAX_RUNNER_NUM:
            break
        id_ = await _create_runner(
            runset_id,
            cloud_account_id,
            i,
            region_id,
            instance_type,
            name_prefix,
            application_id,
            tags,
            destroy_conditions,
            commands,
            token,
            created_at,
            spot_settings,
            open_ingress,
        )
        runners.append(id_)
    # submit tasks
    await submit_tasks(
        runners,
        TaskState.STARTING_PREPARING
    )

    await db.runset.insert_one(d)
    return json(d, status=201)


@app.route('bulldozer/v2/templates/<template_id>/runsets', methods=["GET", ])
async def get_runsets(request, template_id: str):
    """
    get runsets
    :param request:
    :param template_id
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    # TODO: exclude deleted
    res = [doc async for doc in db.runset.find({"token": token, "template_id": template_id})]
    return json(res)


@app.route('/bulldozer/v2/runsets/<id_>', methods=["GET", ])
async def get_runset(request, id_: str):
    """
    gets runsets
    :param request:
    :param id_
    :return:
    """

    token = None
    res = await check_secret(request, False)
    if not res:
        token = await extract_token(request)
        await check_token(token)
    if token:
        o = await db.runset.find_one({"token": token, "_id": id_})
    else:
        o = await db.runset.find_one({"_id": id_})
    if not o:
        raise SanicException("runset not found", status_code=404)
    runners = [doc async for doc in db.runner.find({"runset_id": id_})]

    cost = await CostCalc.run_async(
        cost_calc.calc_runset_cost,
        runners,
    )
    logger.info("cost for runset %s: %f", id_, cost)
    o["cost"] = cost
    return json(o)


@app.route('/bulldozer/v2/runsets/<id_>', methods=["PATCH", ])
async def set_runset_state(request, id_: str):
    """
    sets runset state (stop)
    :param request:
    :param id_
    :return:
    """
    token = None

    res = await check_secret(request, False)
    if not res:
        token = await extract_token(request)
        await check_token(token)
    if token:
        o = await db.runset.find_one({"token": token, "_id": id_})
    else:
        o = await db.runset.find_one({"_id": id_})

    if not o:
        raise SanicException("runset not found", status_code=404)

    doc = request.json
    # TODO: validators?
    state = doc.get("state")
    requestor_runner_id = doc.get("runner_id")

    if state not in [RunsetState.STOPPED]:
        raise SanicException(
            "only stop state is supported", status_code=409)

    if requestor_runner_id:
        # if requestor runner id is set we should skip setting
        # destroy flag for it
        filter = {
                "$and": [
                    {"runset_id": id_},
                    {"_id": {"$nin": [requestor_runner_id]}},
                ]
            }
    else:
        filter = {"runset_id": id_}

    # to avoid conflicting tasks in queue, we just set destroy flag
    # worker will check this flag and destroy if it set
    await db.runner.update_many(filter, {'$set': {
            "destroy": True}})

    await db.runset.update_one({"_id": id_}, {'$set': {
        "state": state}})

    o = await db.runset.find_one({"_id": id_})
    return json(o)


@app.route('/bulldozer/v2/runsets/<id_>/runners', methods=["GET", ])
async def get_runners(request, id_: str):
    """
    get runsets
    :param request:
    :param id_
    :return:
    """
    token = await extract_token(request)
    await check_token(token)
    # TODO: exclude deleted
    runners = [doc async for doc in db.runner.find({"token": token, "runset_id": id_})]
    for runner in runners:
        cost = await CostCalc.run_async(
            cost_calc.calc_runner_cost,
            runner
        )
        runner["cost"] = cost
    return json(runners)


@app.route('/bulldozer/v2/runners/<id_>', methods=["GET", ])
async def get_runner(request, id_: str):
    """
    get runner
    :param request:
    :param id_
    :return:
    """
    # gets runner by secret
    await check_secret(request)
    o = await db.runner.find_one({"_id": id_})
    if not o:
        raise SanicException("runner not found", status_code=404)

    cost = await CostCalc.run_async(
        cost_calc.calc_runner_cost,
        o
    )
    o["cost"] = cost
    return json(o)


@app.route('/bulldozer/v2/runners', methods=["GET", ])
async def bulk_get_runners(request):
    """
    bulk get runners
    :param request:
    :return:
    """
    token = await extract_token(request)
    await check_token(token)

    runset_ids = []
    runset_id = "runset_id"
    args = request.args
    supported_keys = [runset_id]
    if len(args) < 1:
        raise SanicException("at list one param required", status_code=400)
    if not any(filter(lambda x: x in supported_keys, request.args.keys())):
        raise SanicException("%s is required" % runset_id, status_code=400)

    if runset_id in request.args.keys():
        runset_ids = request.args[runset_id]

    runners = [doc async for doc in db.runner.find(
        {"runset_id": {"$in": runset_ids}})]
    for runner in runners:
        cost = await CostCalc.run_async(
            cost_calc.calc_runner_cost,
            runner
        )
        runner["cost"] = cost
    return json(runners)


@app.route('/bulldozer/v2/runners/<id_>', methods=["PATCH", ])
async def update_runner(request, id_: str):
    """
    update runner
    :param request:
    :param id_
    :return:
    """
    # updates runner by secret
    await check_secret(request)
    o = await db.runner.find_one({"_id": id_})
    if not o:
        raise SanicException("run not found", status_code=404)
    doc = request.json
    return_code = doc.get("return_code")
    reason = doc.get("reason")
    instance_id = doc.get("instance_id")
    state = doc.get("state")
    name = doc.get("name")
    ip_addr = doc.get("ip_addr")
    run_id = doc.get("run_id")
    destroyed_at = doc.get("destroyed_at")
    started_at = doc.get("started_at")

    sd = dict()
    if return_code is not None:
        sd.update({"return_code": return_code})

    if reason is not None:
        sd.update({"reason": reason})

    if instance_id is not None:
        sd.update({"instance_id": instance_id})

    if name is not None:
        sd.update({"name": name})

    if state is not None:
        sd.update({"state": state})

    if ip_addr is not None:
        sd.update({"ip_addr": ip_addr})

    if run_id is not None:
        sd.update({"run_id": run_id})

    if destroyed_at is not None:
        sd.update({"destroyed_at": destroyed_at})

    if started_at is not None:
        sd.update({"started_at": started_at})

    if sd:
        await db.runner.update_one(
            {"_id": id_}, {'$set': sd})

    o = await db.runner.find_one({"_id": id_})
    runset_id = o["runset_id"]

    sd = dict()
    runners = [doc async for doc in db.runner.find({"runset_id": runset_id})]
    runset = await db.runset.find_one({"_id": runset_id})
    if not runset.get("started_at", 0):
        started = sorted(
            list(filter(lambda x: x.get("started_at", 0) != 0, runners)),
            key=lambda s: s["started_at"]
        )
        if started:
            started_at = started[0]["started_at"]
            sd.update({"started_at": started_at})
    if not runset.get("destroyed_at", 0):
        if all(map(lambda x: x.get("destroyed_at", 0) != 0, runners)):
            destroyed_at = sorted(
                list(map(lambda x: x, runners)),
                key=lambda s: s["destroyed_at"])[-1]["destroyed_at"]
            sd.update({"destroyed_at": destroyed_at})

    # update runset state
    runner_state_map = {x["_id"]: x["state"] for x in runners}

    # TODO: check usage
    if all(map(lambda x: x["state"] == TaskState.ERROR, runners)):

        sd.update({"state": RunsetState.ERROR})
    elif (any(map(lambda x: x["state"] == TaskState.STARTED, runners)) and not
          all(map(lambda x: x["state"] in [
             TaskState.STARTING_PREPARING,
             TaskState.STARTING,
             TaskState.WAITING_ARCEE,
             TaskState.DESTROYING_SCHEDULED,
             TaskState.DESTROYING], runners))):
        sd.update({"state": RunsetState.STARTED})
    elif any(map(lambda x: x["state"] in [
        TaskState.STARTING_PREPARING,
        TaskState.STARTING,
        TaskState.WAITING_ARCEE
    ], runners)):
        sd.update({"state": RunsetState.RUNNING})
    elif any(map(lambda x: x["state"] in [
        TaskState.DESTROYING_SCHEDULED,
        TaskState.DESTROYING,
        TaskState.DESTROY_PREPARING
    ], runners)):
        sd.update({"state": RunsetState.STOPPING})
    elif (any(map(lambda x: x["state"] == TaskState.DESTROYED, runners)) and not
          all(map(lambda x: x["state"] in [
             TaskState.STARTING_PREPARING,
             TaskState.STARTING,
             TaskState.WAITING_ARCEE,
             TaskState.DESTROYING_SCHEDULED,
             TaskState.DESTROYING], runners))):
        sd.update({"state": RunsetState.STOPPED})
    # log update state map
    logger.info(
        "runset: %s state map: %s, update: %s",
        runset_id,
        str(runner_state_map),
        str(sd)
    )

    if sd:
        await db.runset.update_one(
            {"_id": runset_id}, {'$set': sd})
    return json(o)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8896)
