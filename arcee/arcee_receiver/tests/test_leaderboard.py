import asyncio
import datetime
import json
import uuid
import importlib
import pytest
import sys
from datetime import datetime, timezone
from arcee.arcee_receiver.tests.base import AConfigClMock, DB_MOCK


sys.path.append('.')
TOKEN1 = "token_value1"
TOKEN2 = "token_value2"

LB_URL = '/arcee/v2/applications/{}/leaderboards'


@pytest.fixture
def mock_base(mocker):
    mocker.patch('optscale_client.aconfig_cl.aconfig_cl.AConfigCl',
                 AConfigClMock)
    mocker.patch('arcee.arcee_receiver.server.db', DB_MOCK)


@pytest.fixture
def app(mock_base):
    arcee_app = importlib.import_module('arcee.arcee_receiver.server')
    return arcee_app.app


async def prepare_token():
    await DB_MOCK['token'].insert_one({"token": TOKEN1, "deleted_at": 0})
    await DB_MOCK['token'].insert_one({"token": TOKEN2, "deleted_at": 0})


async def prepare_goals():
    goal1 = {
        "_id": str(uuid.uuid4()),
        "name": "more loss",
        "tendency": "more",
        "target_value": 100,
        "key": "loss",
        "func": "last",
        "token": TOKEN1,
    }
    await DB_MOCK['goal'].insert_one(goal1)
    goal2 = {
        "_id": str(uuid.uuid4()),
        "name": "less accuracy",
        "tendency": "less",
        "target_value": 0,
        "key": "accuracy",
        "func": "last",
        "token": TOKEN1,
    }
    await DB_MOCK['goal'].insert_one(goal2)
    return [x async for x in DB_MOCK['goal'].find()]


async def prepare_apps(goals=None):
    model1 = {
        "_id": str(uuid.uuid4()),
        "owner_id": str(uuid.uuid4()),
        "name": "model1",
        "goals": [],
        "token": TOKEN1,
        "deleted_at": 0
    }
    if goals:
        model1['goals'] = goals
    await DB_MOCK['application'].insert_one(model1)
    model2 = model1.copy()
    model2['_id'] = str(uuid.uuid4())
    await DB_MOCK['application'].insert_one(model2)
    return [x async for x in DB_MOCK['application'].find()]


async def prepare_run(application_id, start, state, number, data):
    run = {
        "_id": str(uuid.uuid4()),
        "application_id": application_id,
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


async def clean_env():
    await DB_MOCK['goal'].drop()
    await DB_MOCK['application'].drop()
    await DB_MOCK['leaderboard'].drop()


@pytest.fixture(autouse=True)
def clean_db_after_test():
    yield
    asyncio.run(clean_env())


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (LB_URL.format(str(uuid.uuid4())), client.get),
        (LB_URL.format(str(uuid.uuid4())), client.post),
        (LB_URL.format(str(uuid.uuid4())), client.get),
        (LB_URL.format(str(uuid.uuid4())), client.patch),
        (LB_URL.format(str(uuid.uuid4())), client.delete),
    ]:
        _, response = await method(path, headers={"x-api-key": "wrong"})
        assert response.status == 401
        assert "Token not found" in response.text

        _, response = await method(path)
        assert response.status == 401
        assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_create_leaderboard(app):
    client = app.asgi_client
    await prepare_token()
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "primary_goal": goals[0]['_id'],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": ['tag']
    }
    _, response = await client.post(LB_URL.format(apps[0]['_id']),
                                    data=json.dumps(lb),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    for key, value in lb.items():
        assert response.json[key] == value
    assert response.json['deleted_at'] == 0
    assert response.json['token'] == TOKEN1

    _, response = await client.post(LB_URL.format(apps[0]['_id']),
                                    data=json.dumps(lb),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 409
    assert "Conflict" in response.text


@pytest.mark.asyncio
async def test_create_invalid_filters(app):
    client = app.asgi_client
    await prepare_token()
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "primary_goal": goals[0]['_id'],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": []
    }

    data = lb.copy()
    data['filters'] = [{"id": "test", "min": 11}]
    _, response = await client.post(LB_URL.format(apps[0]['_id']),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Invalid filters" in response.text

    data = lb.copy()
    data['filters'] = [{"id": goals[1]['_id'], "min": 100, "max": 0}]
    _, response = await client.post(LB_URL.format(apps[0]['_id']),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Invalid min/max filter values" in response.text


@pytest.mark.asyncio
async def test_create_minimum_params(app):
    client = app.asgi_client
    await prepare_token()
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "primary_goal": goals[0]['_id'],
        "group_by_hp": True,
    }

    data = lb.copy()
    _, response = await client.post(LB_URL.format(apps[0]['_id']),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    assert response.json['other_goals'] == []
    assert response.json['grouping_tags'] == []
    assert response.json['filters'] == []


@pytest.mark.asyncio
async def test_create_invalid_application(app):
    client = app.asgi_client
    await prepare_token()
    goals = await prepare_goals()
    lb = {
        "primary_goal": goals[0]['_id'],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": []
    }

    data = lb.copy()
    _, response = await client.post(LB_URL.format(str(uuid.uuid4())),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Application not found" in response.text


@pytest.mark.asyncio
async def test_create_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    goals = await prepare_goals()
    lb = {
        "primary_goal": goals[0]['_id'],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": []
    }

    for param in ['_id', 'created_at', 'deleted_at', 'token', 'test']:
        data = lb.copy()
        data[param] = 'test'
        _, response = await client.post(LB_URL.format(str(uuid.uuid4())),
                                        data=json.dumps(data),
                                        headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text

    data = lb.copy()
    data['filters'] = [{'id': goals[0]['_id'], 'min': 12, 'test': 1}]
    _, response = await client.post(LB_URL.format(str(uuid.uuid4())),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_create_missing_required(app):
    client = app.asgi_client
    await prepare_token()
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "primary_goal": goals[0]['_id'],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": []
    }
    for param in ['primary_goal', 'group_by_hp']:
        data = lb.copy()
        data.pop(param, None)
        _, response = await client.post(LB_URL.format(apps[0]['_id']),
                                        data=json.dumps(data),
                                        headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Field required" in response.text


@pytest.mark.asyncio
async def test_create_invalid_goal(app):
    client = app.asgi_client
    await prepare_token()
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "primary_goal": goals[0]['_id'],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": []
    }
    data = lb.copy()
    data['primary_goal'] = 'fake'
    _, response = await client.post(LB_URL.format(apps[0]['_id']),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "some goals not exists in db:" in response.text

    data = lb.copy()
    data['other_goals'] = ['fake']
    data['filters'] = []
    _, response = await client.post(LB_URL.format(apps[0]['_id']),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "some goals not exists in db:" in response.text


@pytest.mark.asyncio
async def test_get_missing_app(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(LB_URL.format('fake'),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert "{}" in response.text


@pytest.mark.asyncio
async def test_get_deleted(app):
    client = app.asgi_client
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_goal": goals[0]['_id'],
        "application_id": apps[0]['_id'],
        "group_by_hp": False,
        "grouping_tags": [],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "deleted_at": 123,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    _, response = await client.get(LB_URL.format(apps[0]['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert "{}" in response.text


@pytest.mark.asyncio
async def test_get_leaderboard(app):
    client = app.asgi_client
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_goal": goals[0]['_id'],
        "application_id": apps[0]['_id'],
        "group_by_hp": False,
        "grouping_tags": [],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    _, response = await client.get(LB_URL.format(apps[0]['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json == lb


@pytest.mark.asyncio
async def test_patch_invalid_app(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.patch(LB_URL.format(str(uuid.uuid4())),
                                     headers={"x-api-key": TOKEN1},
                                     data="{}")
    assert response.status == 404
    assert "Application not found" in response.text


@pytest.mark.asyncio
async def test_patch_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_goal": goals[0]['_id'],
        "application_id": apps[0]['_id'],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    for param in ['_id', 'created_at', 'deleted_at', 'token', 'test']:
        data = dict()
        data[param] = 'test'
        _, response = await client.post(LB_URL.format(str(uuid.uuid4())),
                                        data=json.dumps(data),
                                        headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text

    data = {'filters': [{'id': goals[0]['_id'], 'min': 12, 'test': 1}]}
    _, response = await client.post(LB_URL.format(str(uuid.uuid4())),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_patch_leaderboard(app):
    client = app.asgi_client
    await prepare_token()
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_goal": goals[0]['_id'],
        "application_id": apps[0]['_id'],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    lb_update = {
        "primary_goal": goals[1]['_id'],
        "other_goals": [],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
    }
    _, response = await client.patch(LB_URL.format(apps[0]['_id']),
                                     headers={"x-api-key": TOKEN1},
                                     data=json.dumps(lb_update))
    assert response.status == 200
    lb.update(lb_update)
    assert response.json == lb


@pytest.mark.asyncio
async def test_patch_invalid_params(app):
    client = app.asgi_client
    await prepare_token()
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_goal": goals[0]['_id'],
        "application_id": apps[0]['_id'],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    for param in ['_id', 'token', 'created_at', 'deleted_at', 'test']:
        _, response = await client.patch(LB_URL.format(apps[0]['_id']),
                                         headers={"x-api-key": TOKEN1},
                                         data=json.dumps({param: 123}))
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text

    for param in ['primary_goal', 'other_goals', 'filters', 'group_by_hp',
                  'grouping_tags']:
        lb_update = {param: 123}
        _, response = await client.patch(LB_URL.format(apps[0]['_id']),
                                         headers={"x-api-key": TOKEN1},
                                         data=json.dumps(lb_update))
        assert response.status == 400
        assert "Input should be a" in response.text


@pytest.mark.asyncio
async def test_patch_invalid_goal(app):
    client = app.asgi_client
    await prepare_token()
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_goal": goals[0]['_id'],
        "application_id": apps[0]['_id'],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    updates = {
        "primary_goal": "fake"
    }
    _, response = await client.patch(LB_URL.format(apps[0]['_id']),
                                     headers={"x-api-key": TOKEN1},
                                     data=json.dumps(updates))
    assert response.status == 400
    assert "some goals not exists in db:" in response.text


@pytest.mark.asyncio
async def test_delete_missing(app):
    client = app.asgi_client
    _, response = await client.delete(LB_URL.format('fake'),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Not found" in response.text


@pytest.mark.asyncio
async def test_delete_leaderboard(app):
    client = app.asgi_client
    goals = await prepare_goals()
    apps = await prepare_apps()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_goal": goals[0]['_id'],
        "application_id": apps[0]['_id'],
        "other_goals": [goals[1]['_id']],
        "filters": [{"id": goals[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    _, response = await client.delete(LB_URL.format(apps[0]['_id']),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json == {'deleted': True, '_id': lb['_id']}
    result = await DB_MOCK['leaderboard'].find_one({'_id': lb['_id']})
    assert result['deleted_at'] != 0
