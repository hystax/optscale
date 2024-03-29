import json
import uuid
import pytest
from arcee.arcee_receiver.tests.base import (
    DB_MOCK, TOKEN1, Urls, prepare_tasks, prepare_metrics, prepare_token,
    prepare_run, prepare_model_version)


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (Urls.tasks, client.post),
        (Urls.tasks, client.get),
        (Urls.task.format(str(uuid.uuid4())), client.patch),
        (Urls.task.format(str(uuid.uuid4())), client.get),
        (Urls.task.format(str(uuid.uuid4())), client.delete),
    ]:
        _, response = await method(path, headers={"x-api-key": "wrong"})
        assert response.status == 401
        assert "Token not found" in response.text

        _, response = await method(path)
        assert response.status == 401
        assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_create_task(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    task = {
        'key': 'key',
        'description': 'description',
        'name': 'name',
        'metrics': [metrics[0]['_id']]
    }
    _, response = await client.post(Urls.tasks,
                                    data=json.dumps(task),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 200
    for key, value in task.items():
        assert response.json[key] == value
    assert response.json['deleted_at'] == 0
    assert response.json['token'] == TOKEN1

    _, response = await client.post(Urls.tasks,
                                    data=json.dumps(task),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 409
    assert "Conflict" in response.text


@pytest.mark.asyncio
async def test_create_task(app):
    client = app.asgi_client
    await prepare_token()
    task = {
        'key': 'key',
        'description': 'description',
        'name': 'name',
        'metrics': ['test']
    }
    _, response = await client.post(Urls.tasks,
                                    data=json.dumps(task),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "some metrics not exists in db:" in response.text


@pytest.mark.asyncio
async def test_create_task_missing_key(app):
    client = app.asgi_client
    await prepare_token()
    task = {
        'description': 'description',
        'name': 'name',
        'metrics': []
    }
    _, response = await client.post(Urls.tasks,
                                    data=json.dumps(task),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Key should be str" in response.text


@pytest.mark.asyncio
async def test_get_tasks(app):
    client = app.asgi_client
    await prepare_token()
    await prepare_tasks()
    _, response = await client.get(Urls.tasks,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200


@pytest.mark.asyncio
async def test_patch_invalid_task(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.patch(Urls.task.format(str(uuid.uuid4())),
                                     headers={"x-api-key": TOKEN1},
                                     data="{}")
    assert response.status == 404
    assert "Not found" in response.text


@pytest.mark.asyncio
async def test_patch_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    for param in ['_id', 'created_at', 'deleted_at', 'token', 'test']:
        data = dict()
        data[param] = 'test'
        _, response = await client.patch(
            Urls.task.format(tasks[0]['_id']),
            data=json.dumps(data),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_patch_task(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    task_update = {
        "name": "new",
        "metrics": [],
        "description": "description",
        "owner_id": str(uuid.uuid4())
    }
    _, response = await client.patch(Urls.task.format(tasks[0]['_id']),
                                     headers={"x-api-key": TOKEN1},
                                     data=json.dumps(task_update))
    assert response.status == 200
    task = await DB_MOCK['task'].find_one({'_id': tasks[0]['_id']})
    for k, v in task_update.items():
        assert v == task[k]


@pytest.mark.asyncio
async def test_patch_invalid_params(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    for param in ['name', 'description', 'owner_id', 'metrics']:
        task_update = {param: 123}
        _, response = await client.patch(
            Urls.task.format(tasks[0]['_id']),
            headers={"x-api-key": TOKEN1},
            data=json.dumps(task_update))
        assert response.status == 400
        assert "Input should be a" in response.text


@pytest.mark.asyncio
async def test_patch_invalid_metric(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    task_update = {
        "metrics": ['test'],
    }
    _, response = await client.patch(Urls.task.format(tasks[0]['_id']),
                                     headers={"x-api-key": TOKEN1},
                                     data=json.dumps(task_update))
    assert response.status == 400
    assert "some metrics not exists in db" in response.text


@pytest.mark.asyncio
async def test_get_task(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    _, response = await client.get(Urls.task.format(tasks[0]['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert 'key' == response.json['key']


@pytest.mark.asyncio
async def test_get_missing_task(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.task.format('fake'),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Not found" in response.text


@pytest.mark.asyncio
async def test_delete_task(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    model_version = await prepare_model_version('model_id', run['_id'])
    _, response = await client.delete(
        Urls.task.format(tasks[0]['_id']),
        headers={"x-api-key": TOKEN1})
    assert response.status == 200
    task = await DB_MOCK['task'].find_one({'_id': tasks[0]['_id']})
    assert task['deleted_at'] != 0
    version = await DB_MOCK['model_version'].find_one(
        {'_id': model_version['_id']})
    assert version['deleted_at'] != 0


@pytest.mark.asyncio
async def test_delete_missing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.delete(Urls.task.format('fake'),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Not found" in response.text
