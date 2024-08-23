import uuid
from datetime import datetime, timezone
from mongomock_motor import AsyncMongoMockClient
from optscale_client.aconfig_cl.aconfig_cl import AConfigCl


DB_MOCK = AsyncMongoMockClient()['arcee']

TOKEN1 = "token_value1"
TOKEN2 = "token_value2"
SECRET = "secret"


class AConfigClMock(AConfigCl):

    async def arcee_params(self):
        return 'name', 'password', '127.0.0.1', 80, 'arcee'

    async def cluster_secret(self):
        return SECRET


class Urls:
    leaderboard_templates = '/arcee/v2/tasks/{}/leaderboard_templates'
    leaderboard_template = '/arcee/v2/leaderboard_templates/{}'
    leaderboards = '/arcee/v2/leaderboard_templates/{}/leaderboards'
    leaderboard = '/arcee/v2/leaderboards/{}'
    tasks = '/arcee/v2/tasks'
    task = '/arcee/v2/tasks/{}'
    models = '/arcee/v2/models'
    model = '/arcee/v2/models/{}'
    model_version = '/arcee/v2/runs/{0}/models/{1}/version'
    task_model_version = '/arcee/v2/tasks/{}/model_versions'
    runs = '/arcee/v2/tasks/{}/run'
    run = '/arcee/v2/run/{}'
    metrics = '/arcee/v2/metrics'
    metric = '/arcee/v2/metrics/{}'
    collect = '/arcee/v2/collect'
    artifacts = '/arcee/v2/artifacts'
    artifact = '/arcee/v2/artifacts/{}'
    tags = '/arcee/v2/tasks/{}/tags'
    datasets = '/arcee/v2/datasets'
    dataset_register = '/arcee/v2/run/{}/dataset_register'
    dataset = '/arcee/v2/datasets/{}'
    labels = '/arcee/v2/labels'
    tokens = '/arcee/v2/tokens'
    token = '/arcee/v2/tokens/{}'


async def prepare_token():
    await DB_MOCK['token'].insert_one(
        {"_id": str(uuid.uuid4()), "token": TOKEN1, "deleted_at": 0})
    await DB_MOCK['token'].insert_one(
        {"_id": str(uuid.uuid4()), "token": TOKEN2, "deleted_at": 0})
    return [x async for x in DB_MOCK['token'].find({})]


async def prepare_tasks(metrics=None):
    task1 = {
        "_id": str(uuid.uuid4()),
        "owner_id": str(uuid.uuid4()),
        "key": "key",
        "name": "task",
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


async def prepare_run(task_id, start=1, state=1, number=1, data=None,
                      tags=None):
    if not data:
        data = {}
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
    if tags:
        run['tags'] = tags
    await DB_MOCK['run'].insert_one(run)
    return await DB_MOCK['run'].find_one({'_id': run['_id']})


async def prepare_leaderboard_template(
        primary_metric, task_id, other_metrics=None, filters=None,
        group_by_hp=False, grouping_tags=None):
    if other_metrics is None:
        other_metrics = []
    if filters is None:
        filters = []
    if grouping_tags is None:
        grouping_tags = []
    lb_template = {
        "_id": str(uuid.uuid4()),
        "primary_metric": primary_metric,
        "other_metrics": other_metrics,
        "filters": filters,
        "group_by_hp": group_by_hp,
        "grouping_tags": grouping_tags,
        "task_id": task_id,
        "token": TOKEN1,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "deleted_at": 0
    }
    await DB_MOCK['leaderboard_template'].insert_one(lb_template)
    return await DB_MOCK['leaderboard_template'].find_one(
        {'_id': lb_template['_id']})


async def prepare_leaderboard(leaderboard_template_id, name=None,
                              dataset_ids=None):
    if dataset_ids is None:
        dataset_ids = []
    leaderboard = {
        "_id": str(uuid.uuid4()),
        "leaderboard_template_id": leaderboard_template_id,
        "name": name or 'test',
        "dataset_ids": dataset_ids,
        "token": TOKEN1,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "deleted_at": 0
    }
    await DB_MOCK['leaderboard'].insert_one(leaderboard)
    return await DB_MOCK['leaderboard'].find_one(
        {'_id': leaderboard['_id']})


async def prepare_dataset(name=None, description=None, labels=None, path=None):
    if labels is None:
        labels = []
    dataset = {
        "_id": str(uuid.uuid4()),
        "name": name or 'test',
        "description": description or 'test',
        "labels": labels,
        "path": path or 'test',
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1,
        "deleted_at": 0
    }
    await DB_MOCK['dataset'].insert_one(dataset)
    return await DB_MOCK['dataset'].find_one({'_id': dataset['_id']})


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


async def prepare_artifact(run_id, name=None, description=None,
                           path=None, tags=None, created_at=None):
    now = datetime.now(tz=timezone.utc)
    if not created_at:
        created_at = int(now.timestamp())
    if not name:
        name = "my artifact"
    if not description:
        description = "my artifact"
    if not path:
        path = "/my/path"
    if not tags:
        tags = {"key": "value"}
    artifact = {
        "_id": str(uuid.uuid4()),
        "path": path,
        "name": name,
        "description": description,
        "tags": tags,
        "run_id": run_id,
        "created_at": created_at,
        "token": TOKEN1,
        '_created_at_dt': int(now.replace(hour=0, minute=0, second=0,
                                          microsecond=0).timestamp())
    }
    await DB_MOCK['artifact'].insert_one(artifact)
    return await DB_MOCK['artifact'].find_one({'_id': artifact['_id']})
