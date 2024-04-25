import datetime
import json
import uuid
import pytest
import sys
from datetime import datetime, timezone
from arcee.arcee_receiver.tests.base import (
    DB_MOCK, TOKEN1, Urls, prepare_tasks, prepare_metrics, prepare_token)


sys.path.append('.')


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (Urls.leaderboards.format(str(uuid.uuid4())), client.get),
        (Urls.leaderboards.format(str(uuid.uuid4())), client.post),
        (Urls.leaderboards.format(str(uuid.uuid4())), client.get),
        (Urls.leaderboards.format(str(uuid.uuid4())), client.patch),
        (Urls.leaderboards.format(str(uuid.uuid4())), client.delete),
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
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": ['tag']
    }
    _, response = await client.post(Urls.leaderboards.format(tasks[0]['_id']),
                                    data=json.dumps(lb),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    for key, value in lb.items():
        assert response.json[key] == value
    assert response.json['deleted_at'] == 0
    assert response.json['token'] == TOKEN1

    _, response = await client.post(Urls.leaderboards.format(tasks[0]['_id']),
                                    data=json.dumps(lb),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 409
    assert "Conflict" in response.text


@pytest.mark.asyncio
async def test_create_invalid_filters(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": []
    }

    data = lb.copy()
    data['filters'] = [{"id": "test", "min": 11}]
    _, response = await client.post(Urls.leaderboards.format(tasks[0]['_id']),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Invalid filters" in response.text

    data = lb.copy()
    data['filters'] = [{"id": metrics[1]['_id'], "min": 100, "max": 0}]
    _, response = await client.post(Urls.leaderboards.format(tasks[0]['_id']),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Invalid min/max filter values" in response.text


@pytest.mark.asyncio
async def test_create_minimum_params(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "primary_metric": metrics[0]['_id'],
        "group_by_hp": True,
    }

    data = lb.copy()
    _, response = await client.post(Urls.leaderboards.format(tasks[0]['_id']),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    assert response.json['other_metrics'] == []
    assert response.json['grouping_tags'] == []
    assert response.json['filters'] == []


@pytest.mark.asyncio
async def test_create_invalid_task(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    lb = {
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": []
    }

    data = lb.copy()
    _, response = await client.post(
        Urls.leaderboards.format(str(uuid.uuid4())),
        data=json.dumps(data),
        headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Task not found" in response.text


@pytest.mark.asyncio
async def test_create_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    lb = {
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": []
    }

    for param in ['_id', 'created_at', 'deleted_at', 'token', 'test']:
        data = lb.copy()
        data[param] = 'test'
        _, response = await client.post(
            Urls.leaderboards.format(str(uuid.uuid4())),
            data=json.dumps(data),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text

    data = lb.copy()
    data['filters'] = [{'id': metrics[0]['_id'], 'min': 12, 'test': 1}]
    _, response = await client.post(
        Urls.leaderboards.format(str(uuid.uuid4())),
        data=json.dumps(data),
        headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_create_missing_required(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": []
    }
    for param in ['primary_metric', 'group_by_hp']:
        data = lb.copy()
        data.pop(param, None)
        _, response = await client.post(
            Urls.leaderboards.format(tasks[0]['_id']),
            data=json.dumps(data),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Field required" in response.text


@pytest.mark.asyncio
async def test_create_invalid_metric(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": []
    }
    data = lb.copy()
    data['primary_metric'] = 'fake'
    _, response = await client.post(Urls.leaderboards.format(tasks[0]['_id']),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "some metrics not exists in db:" in response.text

    data = lb.copy()
    data['other_metrics'] = ['fake']
    data['filters'] = []
    _, response = await client.post(Urls.leaderboards.format(tasks[0]['_id']),
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "some metrics not exists in db:" in response.text


@pytest.mark.asyncio
async def test_get_missing_task(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.leaderboards.format('fake'),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert "{}" in response.text


@pytest.mark.asyncio
async def test_get_deleted(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_metric": metrics[0]['_id'],
        "task_id": tasks[0]['_id'],
        "group_by_hp": False,
        "grouping_tags": [],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "deleted_at": 123,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    _, response = await client.get(Urls.leaderboards.format(tasks[0]['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert "{}" in response.text


@pytest.mark.asyncio
async def test_get_leaderboard(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_metric": metrics[0]['_id'],
        "task_id": tasks[0]['_id'],
        "group_by_hp": False,
        "grouping_tags": [],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    _, response = await client.get(Urls.leaderboards.format(tasks[0]['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json == lb


@pytest.mark.asyncio
async def test_patch_invalid_task(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.patch(
        Urls.leaderboards.format(str(uuid.uuid4())),
        headers={"x-api-key": TOKEN1},
        data="{}")
    assert response.status == 404
    assert "Task not found" in response.text


@pytest.mark.asyncio
async def test_patch_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_metric": metrics[0]['_id'],
        "task_id": tasks[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
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
        _, response = await client.post(
            Urls.leaderboards.format(str(uuid.uuid4())),
            data=json.dumps(data),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text

    data = {'filters': [{'id': metrics[0]['_id'], 'min': 12, 'test': 1}]}
    _, response = await client.post(
        Urls.leaderboards.format(str(uuid.uuid4())),
        data=json.dumps(data),
        headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_patch_leaderboard(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_metric": metrics[0]['_id'],
        "task_id": tasks[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    lb_update = {
        "primary_metric": metrics[1]['_id'],
        "other_metrics": [],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
    }
    _, response = await client.patch(Urls.leaderboards.format(tasks[0]['_id']),
                                     headers={"x-api-key": TOKEN1},
                                     data=json.dumps(lb_update))
    assert response.status == 200
    lb.update(lb_update)
    assert response.json == lb


@pytest.mark.asyncio
async def test_patch_leaderboard_group_by_hp(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_metric": metrics[0]['_id'],
        "task_id": tasks[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    lb_update = {
        "group_by_hp": False
    }
    _, response = await client.patch(Urls.leaderboards.format(tasks[0]['_id']),
                                     headers={"x-api-key": TOKEN1},
                                     data=json.dumps(lb_update))
    assert response.status == 200
    assert response.json['group_by_hp'] is False


@pytest.mark.asyncio
async def test_patch_invalid_params(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_metric": metrics[0]['_id'],
        "task_id": tasks[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    for param in ['_id', 'token', 'created_at', 'deleted_at', 'test']:
        _, response = await client.patch(
            Urls.leaderboards.format(tasks[0]['_id']),
            headers={"x-api-key": TOKEN1},
            data=json.dumps({param: 123}))
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text

    for param in ['primary_metric', 'other_metrics', 'filters', 'group_by_hp',
                  'grouping_tags']:
        lb_update = {param: 123}
        _, response = await client.patch(
            Urls.leaderboards.format(tasks[0]['_id']),
            headers={"x-api-key": TOKEN1},
            data=json.dumps(lb_update))
        assert response.status == 400
        assert "Input should be a" in response.text


@pytest.mark.asyncio
async def test_patch_invalid_metric(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_metric": metrics[0]['_id'],
        "task_id": tasks[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    updates = {
        "primary_metric": "fake"
    }
    _, response = await client.patch(Urls.leaderboards.format(tasks[0]['_id']),
                                     headers={"x-api-key": TOKEN1},
                                     data=json.dumps(updates))
    assert response.status == 400
    assert "some metrics not exists in db:" in response.text


@pytest.mark.asyncio
async def test_delete_missing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.delete(Urls.leaderboards.format('fake'),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Not found" in response.text


@pytest.mark.asyncio
async def test_delete_leaderboard(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks()
    lb = {
        "_id": str(uuid.uuid4()),
        "primary_metric": metrics[0]['_id'],
        "task_id": tasks[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": [],
        "deleted_at": 0,
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1
    }
    await DB_MOCK['leaderboard'].insert_one(lb)
    _, response = await client.delete(
        Urls.leaderboards.format(tasks[0]['_id']),
        headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json == {'deleted': True, '_id': lb['_id']}
    result = await DB_MOCK['leaderboard'].find_one({'_id': lb['_id']})
    assert result['deleted_at'] != 0
