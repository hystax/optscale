import uuid
from datetime import datetime, timezone
from mongomock_motor import AsyncMongoMockClient
from optscale_client.aconfig_cl.aconfig_cl import AConfigCl


DB_MOCK = AsyncMongoMockClient()['arcee']

TOKEN1 = "token_value1"
TOKEN2 = "token_value2"


class AConfigClMock(AConfigCl):

    async def arcee_params(self):
        return 'name', 'password', '127.0.0.1', 80, 'arcee'

    async def cluster_secret(self):
        return 'secret'


class Urls:
    leaderboards = '/arcee/v2/tasks/{}/leaderboards'
    tasks = '/arcee/v2/tasks'
    task = '/arcee/v2/tasks/{}'
    models = '/arcee/v2/models'
    model = '/arcee/v2/models/{}'
    model_version = '/arcee/v2/models/{0}/runs/{1}'
    task_model_version = '/arcee/v2/tasks/{}/model_versions'
    runs = '/arcee/v2/tasks/{}/run'
    run = '/arcee/v2/run/{}'
    metrics = '/arcee/v2/metrics'
    metric = '/arcee/v2/metrics/{}'


async def prepare_token():
    await DB_MOCK['token'].insert_one(
        {"_id": str(uuid.uuid4()), "token": TOKEN1, "deleted_at": 0})
    await DB_MOCK['token'].insert_one(
        {"_id": str(uuid.uuid4()), "token": TOKEN2, "deleted_at": 0})


async def prepare_tasks(metrics=None):
    task1 = {
        "_id": str(uuid.uuid4()),
        "owner_id": str(uuid.uuid4()),
        "key": "key",
        "name": "model1",
        "metrics": [],
        "token": TOKEN1,
        "deleted_at": 0
    }
    if metrics:
        task1['metrics'] = metrics
    await DB_MOCK['task'].insert_one(task1)
    task2 = task1.copy()
    task2['_id'] = str(uuid.uuid4())
    await DB_MOCK['task'].insert_one(task2)
    return [x async for x in DB_MOCK['task'].find()]


async def prepare_metrics():
    metric1 = {
        "_id": str(uuid.uuid4()),
        "name": "more loss",
        "tendency": "more",
        "target_value": 100,
        "key": "loss",
        "func": "last",
        "token": TOKEN1,
    }
    await DB_MOCK['metric'].insert_one(metric1)
    metric2 = {
        "_id": str(uuid.uuid4()),
        "name": "less accuracy",
        "tendency": "less",
        "target_value": 0,
        "key": "accuracy",
        "func": "last",
        "token": TOKEN1,
    }
    await DB_MOCK['metric'].insert_one(metric2)
    return [x async for x in DB_MOCK['metric'].find()]


async def prepare_run(task_id, start, state, number, data):
    run = {
        "_id": str(uuid.uuid4()),
        "task_id": task_id,
        "name": start,
        "start": start,
        "state": state,
        "number": number,
        "imports": [],
        "deleted_at": 0,
        "data": data,
        "executors": ["executor"]
    }
    await DB_MOCK['run'].insert_one(run)
    return await DB_MOCK['run'].find_one({'_id': run['_id']})


async def prepare_model(token=TOKEN1, key="key"):
    model = {
        "_id": str(uuid.uuid4()),
        "token": token,
        "key": key,
        "name": "my model",
        "description": "",
        "tags": {},
        "created_at": int(datetime.now(tz=timezone.utc).timestamp())
    }
    await DB_MOCK['model'].insert_one(model)
    return await DB_MOCK['model'].find_one({'_id': model['_id']})


async def prepare_model_version(model_id, run_id, version='1', aliases=None,
                                created_at=None, tags=None, deleted_at=0):
    if not aliases:
        aliases = ["best_run"]
    if not tags:
        tags = {}
    if not created_at:
        created_at = int(datetime.now(tz=timezone.utc).timestamp())
    model_version = {
        "_id": str(uuid.uuid4()),
        "version": version,
        "aliases": aliases,
        "path": "/my/path",
        "tags": tags,
        "run_id": run_id,
        "model_id": model_id,
        "deleted_at": deleted_at,
        "created_at": created_at
    }
    await DB_MOCK['model_version'].insert_one(model_version)
    return await DB_MOCK['model_version'].find_one({
        "run_id": run_id, "model_id": model_id})
