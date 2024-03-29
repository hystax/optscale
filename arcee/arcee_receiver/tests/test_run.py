import json
import uuid
import pytest
from arcee.arcee_receiver.tests.base import (
    DB_MOCK, Urls, TOKEN1, prepare_token, prepare_run, prepare_model_version,
    prepare_tasks
)


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (Urls.runs.format(str(uuid.uuid4())), client.post),
        (Urls.runs.format(str(uuid.uuid4())), client.get),
        (Urls.run.format(str(uuid.uuid4())), client.get),
        (Urls.run.format(str(uuid.uuid4())), client.patch),
        (Urls.run.format(str(uuid.uuid4())), client.delete),
    ]:
        _, response = await method(path, headers={"x-api-key": "wrong"})
        assert response.status == 401
        assert "Token not found" in response.text

        _, response = await method(path)
        assert response.status == 401
        assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_create_run(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = {
        "git": {
            'remote': 'test',
            'branch': 'test',
            'commit_id': 'test',
            'status': 'test'
        },
        "name": "my model",
        "command": "my command",
        "imports": ['import'],
    }
    _, response = await client.post(Urls.runs.format(tasks[0]['key']),
                                    data=json.dumps(run),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 200
    run_id = response.json['id']
    assert run_id

    _, response = await client.post(Urls.runs.format(tasks[0]['key']),
                                    data=json.dumps(run),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 200
    run_id2 = response.json['id']
    assert run_id != run_id2


@pytest.mark.asyncio
async def test_create_required_params(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = {
        "name": "name",
    }
    _, response = await client.post(Urls.runs.format(tasks[0]['key']),
                                    data=json.dumps(run),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert 'Field required' in response.text

    run = {
        "command": "command",
    }
    _, response = await client.post(Urls.runs.format(tasks[0]['key']),
                                    data=json.dumps(run),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert 'Field required' in response.text


@pytest.mark.asyncio
async def test_create_invalid_params_types(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = {
        "git": {
            'remote': 'test',
            'branch': 'test',
            'commit_id': 'test',
            'status': 'test'
        },
        "name": "my model",
        "command": "my command",
        "imports": ['import'],
    }

    for param in ["command", "name"]:
        for value in [1, {"test": 1}, ['test']]:
            params = run.copy()
            params[param] = value
            _, response = await client.post(
                Urls.runs.format(tasks[0]['key']), data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text

    for value in [1, "test", {'test': 'test'}]:
        params = run.copy()
        params['imports'] = value
        _, response = await client.post(
            Urls.runs.format(tasks[0]['key']), data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid list" in response.text

    for value in [1, "test", ['test']]:
        params = run.copy()
        params['git'] = value
        _, response = await client.post(
            Urls.runs.format(tasks[0]['key']), data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid dictionary" in response.text


@pytest.mark.asyncio
async def test_create_invalid_git(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = {
        "git": {
            'remote': 'test',
            'branch': 'test',
            'commit_id': 'test',
            'status': 'test'
        },
        "name": "my model",
        "command": "my command",
        "imports": ['import'],
    }
    params = run.copy()
    params['git'] = {'test': 'test'}
    _, response = await client.post(
        Urls.runs.format(tasks[0]['key']), data=json.dumps(params),
        headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Field required" in response.text

    for param in ["remote", "branch", "commit_id", "status"]:
        for value in [1, {"test": 1}, ['test']]:
            params = run.copy()
            params['git'][param] = value
            _, response = await client.post(
                Urls.runs.format(tasks[0]['key']), data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text


@pytest.mark.asyncio
async def test_list_runs(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    _, response = await client.get(Urls.runs.format(tasks[0]['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 1
    assert response.json[0]['_id'] == run['_id']


@pytest.mark.asyncio
async def test_list_task_runs_empty(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    _, response = await client.get(Urls.runs.format(tasks[0]['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 0


@pytest.mark.asyncio
async def test_create_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = {
        "git": {
            'remote': 'test',
            'branch': 'test',
            'commit_id': 'test',
            'status': 'test'
        },
        "name": "my model",
        "command": "my command",
        "imports": ['import'],
    }

    for param in ['_id', 'task_id', 'start', 'number', 'executors', 'test']:
        data = run.copy()
        data[param] = 'test'
        _, response = await client.post(
            Urls.runs.format(tasks[0]['key']), data=json.dumps(data),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_patch_empty(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    _, response = await client.patch(Urls.run.format(run['_id']),
                                     data=json.dumps({}),
                                     headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json == {"updated": True, "id": run['_id']}


@pytest.mark.asyncio
async def test_patch_invalid_params_types(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    for param in ["reason", "runset_id", "runset_name"]:
        for value in [1, {"test": 1}, ['test']]:
            updates = {
                param: value
            }
            _, response = await client.patch(Urls.run.format(run['_id']),
                                             data=json.dumps(updates),
                                             headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text

    for param in ["tags", "hyperparameters"]:
        for value in [1, "test", ['test']]:
            updates = {
                param: value
            }
            _, response = await client.patch(Urls.run.format(run['_id']),
                                             data=json.dumps(updates),
                                             headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid dictionary" in response.text

    for value in [48, "test", ['test']]:
        updates = {
            "finish": value
        }
        _, response = await client.patch(Urls.run.format(run['_id']),
                                         data=json.dumps(updates),
                                         headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid boolean" in response.text

    for value in [1.11, "test", ['test']]:
        updates = {
            "state": value
        }
        _, response = await client.patch(Urls.run.format(run['_id']),
                                         data=json.dumps(updates),
                                         headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid integer" in response.text


@pytest.mark.asyncio
async def test_patch_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    for param in ['_id', 'task_id', 'start', 'number', 'executors', 'test']:
        data = {param: 'test'}
        _, response = await client.patch(
            Urls.run.format(run['_id']), data=json.dumps(data),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_patch_run(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    updates = {
        "finish": True,
        "hyperparameters": {"key": "value"},
        "tags": {"key": "value"},
        "reason": "reason",
        "state": 1,
        "runset_id": "runset_id",
        "runset_name": "runset_name"
    }
    _, response = await client.patch(Urls.run.format(run['_id']),
                                     data=json.dumps(updates),
                                     headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json == {"updated": True, "id": run['_id']}


@pytest.mark.asyncio
async def test_patch_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    updates = {
        "state": 1
    }
    _, response = await client.patch(Urls.run.format('run'),
                                     data=json.dumps(updates),
                                     headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Run not found" in response.text


@pytest.mark.asyncio
async def test_get_run(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    _, response = await client.get(Urls.run.format(run['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    for key, value in run.items():
        assert response.json[key] == value


@pytest.mark.asyncio
async def test_get_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.run.format('run_id'),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Not found" in response.text


@pytest.mark.asyncio
async def test_delete_run(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    version = await prepare_model_version('model_id', run['_id'])
    _, response = await client.delete(Urls.run.format(run['_id']),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 200
    run_db = await DB_MOCK['run'].find_one({'_id': run['_id']})
    assert run_db is None
    version = await DB_MOCK['model_version'].find_one(
        {'_id': version['_id']})
    assert version['deleted_at'] != 0


@pytest.mark.asyncio
async def test_delete_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.delete(Urls.run.format('run'),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Not found" in response.text
