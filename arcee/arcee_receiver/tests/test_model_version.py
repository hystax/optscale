import json
import uuid
import pytest
from arcee.arcee_receiver.tests.base import (
    DB_MOCK, Urls, TOKEN1, prepare_token, prepare_model, prepare_run,
    prepare_tasks, prepare_model_version)


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (Urls.model_version.format(str(uuid.uuid4()), str(uuid.uuid4())),
         client.post),
        (Urls.model_version.format(str(uuid.uuid4()), str(uuid.uuid4())),
         client.patch),
        (Urls.model_version.format(str(uuid.uuid4()), str(uuid.uuid4())),
         client.delete),
        (Urls.task_model_version.format(str(uuid.uuid4())),
         client.get),
    ]:
        _, response = await method(path, headers={"x-api-key": "wrong"})
        assert response.status == 401
        assert "Token not found" in response.text

        _, response = await method(path)
        assert response.status == 401
        assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_create_model_version(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('app_id', 0, 1, 1, {})
    model_version = {
        "version": "11",
        "aliases": ["best_run"],
        "path": "/my/path",
        "tags": {"my": "tag"}
    }
    _, response = await client.post(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps(model_version), headers={"x-api-key": TOKEN1})
    assert response.status == 201
    for key, value in model_version.items():
        assert response.json[key] == value
    assert response.json['model_id'] == model['_id']
    assert response.json['run_id'] == run['_id']
    assert response.json['created_at'] > 0


@pytest.mark.asyncio
async def test_create_model_without_version(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('app_id', 0, 1, 1, {})
    model_version = {
        "path": "/my/path"
    }
    _, response = await client.post(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps(model_version), headers={"x-api-key": TOKEN1})
    assert response.status == 201
    for key, value in model_version.items():
        assert response.json[key] == value
    assert response.json['model_id'] == model['_id']
    assert response.json['run_id'] == run['_id']
    assert response.json['version'] == '1'
    assert response.json['aliases'] == []


@pytest.mark.asyncio
async def test_create_model_switch_version(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    await prepare_model_version(model['_id'], 'test')
    model_version = {
        "aliases": ["best_run"],
        "path": "/my/path"
    }
    _, response = await client.post(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps(model_version), headers={"x-api-key": TOKEN1})
    assert response.status == 201
    for key, value in model_version.items():
        assert response.json[key] == value
    assert response.json['model_id'] == model['_id']
    assert response.json['run_id'] == run['_id']
    assert response.json['version'] == '2'

    run = await prepare_run('task_id', 0, 1, 1, {})
    model_version = {
        "version": "1"
    }
    _, response = await client.post(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps(model_version), headers={"x-api-key": TOKEN1})
    assert response.status == 201
    assert response.json['version'] == '3'


@pytest.mark.asyncio
async def test_create_aliases(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run1 = await prepare_run('task_id', 0, 1, 1, {})
    run2 = await prepare_run('task_id', 0, 1, 1, {})
    model_version = {
        "version": "1",
        "aliases": ["best_run"]
    }
    _, response = await client.post(
        Urls.model_version.format(model['_id'], run1['_id']),
        data=json.dumps(model_version), headers={"x-api-key": TOKEN1})
    assert response.status == 201
    for key, value in model_version.items():
        assert response.json[key] == value

    model_version2 = {
        "version": "2",
        "aliases": ["best_run", "winner", "best_run"]
    }
    _, response = await client.post(
        Urls.model_version.format(model['_id'], run2['_id']),
        data=json.dumps(model_version2), headers={"x-api-key": TOKEN1})
    assert response.status == 201
    assert response.json['version'] == model_version2['version']
    assert response.json['aliases'] == list(set(model_version2['aliases']))
    version = await DB_MOCK['model_version'].find_one({"run_id": run1['_id']})
    assert version['aliases'] == []

    run3 = await prepare_run('task_id', 0, 1, 1, {})
    model_version = {
        "version": "12"
    }
    _, response = await client.post(
        Urls.model_version.format(model['_id'], run3['_id']),
        data=json.dumps(model_version), headers={"x-api-key": TOKEN1})
    assert response.status == 201
    assert version['aliases'] == []


@pytest.mark.asyncio
async def test_create_invalid_model(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    model_version = {
        "version": "11",
        "aliases": ["best_run"],
        "path": "/my/path"
    }
    _, response = await client.post(
        Urls.model_version.format(model['_id'], 'run_id'),
        data=json.dumps(model_version), headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Run not found" in response.text


@pytest.mark.asyncio
async def test_create_invalid_run(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id', 0, 1, 1, {})
    model_version = {
        "version": "11",
        "aliases": ["best_run"],
        "path": "/my/path"
    }
    _, response = await client.post(
        Urls.model_version.format("model_id", run['_id']),
        data=json.dumps(model_version), headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Model not found" in response.text


@pytest.mark.asyncio
async def test_create_invalid_params(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    for param in ['version', 'path']:
        for value in [1, ["1"], {"1": "1"}]:
            params = {param: value}
            _, response = await client.post(
                Urls.model_version.format(model['_id'], run['_id']),
                data=json.dumps(params), headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert 'Input should be a valid string' in response.text

    for value in [1, "1", {"1": "1"}]:
        params = {'aliases': value}
        _, response = await client.post(
            Urls.model_version.format(model['_id'], run['_id']),
            data=json.dumps(params), headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Input should be a valid list' in response.text

    for value in [1, "1", ["1"]]:
        params = {'tags': value}
        _, response = await client.post(
            Urls.model_version.format(model['_id'], run['_id']),
            data=json.dumps(params), headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Input should be a valid dictionary' in response.text


@pytest.mark.asyncio
async def test_create_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    model_version = {
        "version": "11",
        "aliases": ["best_run"],
        "path": "/my/path"
    }
    for param in ['_id', 'deleted_at', 'run_id', 'model_id', 'test']:
        data = model_version.copy()
        data[param] = 'test'
        _, response = await client.post(
            Urls.model_version.format(model['_id'], run['_id']),
            data=json.dumps(data),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_patch_empty(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    await prepare_model_version(model['_id'], run['_id'])
    _, response = await client.patch(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps({}),
        headers={"x-api-key": TOKEN1})
    assert response.status == 200


@pytest.mark.asyncio
async def test_patch_invalid_params_types(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    await prepare_model_version(model['_id'], run['_id'])
    for param in ['version', 'path']:
        for value in [1, ["1"], {"1": "1"}]:
            params = {param: value}
            _, response = await client.post(
                Urls.model_version.format(model['_id'], run['_id']),
                data=json.dumps(params), headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert 'Input should be a valid string' in response.text

    for value in [1, "1", {"1": "1"}]:
        params = {'aliases': value}
        _, response = await client.post(
            Urls.model_version.format(model['_id'], run['_id']),
            data=json.dumps(params), headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Input should be a valid list' in response.text

    for value in [1, "1", ["1"]]:
        params = {'tags': value}
        _, response = await client.post(
            Urls.model_version.format(model['_id'], run['_id']),
            data=json.dumps(params), headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Input should be a valid dictionary' in response.text


@pytest.mark.asyncio
async def test_patch_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    await prepare_model_version(model['_id'], run['_id'])
    for param in ['_id', 'deleted_at', 'run_id', 'model_id', 'test']:
        updates = {param: 'test'}
        _, response = await client.patch(
            Urls.model_version.format(model['_id'], run['_id']),
            data=json.dumps(updates),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_patch_model(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    await prepare_model_version(model['_id'], run['_id'])
    updates = {
        "version": "11",
        "aliases": ["best_run", "best_run"],
        "path": "/my/path"
    }
    _, response = await client.patch(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps(updates), headers={"x-api-key": TOKEN1})
    assert response.status == 200
    new = {
        "version": "11",
        "aliases": ["best_run"],
        "path": "/my/path"
    }
    for key, value in new.items():
        assert response.json[key] == value


@pytest.mark.asyncio
async def test_patch_tags(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    await prepare_model_version(model['_id'], run['_id'], aliases=['1'])
    updates = {
        "tags": {"test": "test"}
    }
    _, response = await client.patch(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps(updates), headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['tags'] == updates['tags']
    assert response.json['aliases'] == ['1']


@pytest.mark.asyncio
async def test_patch_empty_aliases(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    await prepare_model_version(model['_id'], run['_id'], aliases=['1'])
    updates = {
        "tags": {"1": "2"},
        "aliases": []
    }
    _, response = await client.patch(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps(updates), headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['aliases'] == []


@pytest.mark.asyncio
async def test_patch_version(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    await prepare_model_version(model['_id'], run['_id'])
    updates = {
        "version": "1"
    }
    _, response = await client.patch(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps(updates), headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['version'] == '1'

    updates = {
        "version": "2"
    }
    _, response = await client.patch(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps(updates), headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['version'] == '2'

    updates = {
        "path": "new path"
    }
    _, response = await client.patch(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps(updates), headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['version'] == '2'
    assert response.json['path'] == updates['path']


@pytest.mark.asyncio
async def test_patch_version_with_alias(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    version1 = await prepare_model_version(model['_id'], run['_id'],
                                           aliases=['alias'])
    run2 = await prepare_run('task_id', 0, 1, 1, {})
    await prepare_model_version(model['_id'], run2['_id'], aliases=[])
    updates = {
        "aliases": ["alias"]
    }
    _, response = await client.patch(
        Urls.model_version.format(model['_id'], run2['_id']),
        data=json.dumps(updates), headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['aliases'] == ["alias"]
    version1 = await DB_MOCK['model_version'].find_one(
        {"_id": version1['_id']})
    assert version1['aliases'] == []


@pytest.mark.asyncio
async def test_patch_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    updates = {
        "aliases": ["my_run"],
    }
    _, response = await client.patch(
        Urls.model_version.format(model['_id'], run['_id']),
        data=json.dumps(updates), headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Model version not found" in response.text


@pytest.mark.asyncio
async def test_patch_not_existing_model(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id', 0, 1, 1, {})
    await prepare_model_version('test', run['_id'])
    updates = {
        "aliases": ["best_run"],
    }
    _, response = await client.patch(
        Urls.model_version.format('test', run['_id']),
        data=json.dumps(updates), headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Model not found" in response.text


@pytest.mark.asyncio
async def test_delete_model_version(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    model_id = model['_id']
    run = await prepare_run('task_id', 0, 1, 1, {})
    run_id = run['_id']
    await prepare_model_version(model_id, run_id)
    _, response = await client.delete(
        Urls.model_version.format(model_id, run_id),
        headers={"x-api-key": TOKEN1})
    assert response.status == 204
    assert DB_MOCK['model_version'].find({"run_id": run_id,
                                          "model_id": model_id})


@pytest.mark.asyncio
async def test_delete_not_existing_model(app):
    client = app.asgi_client
    await prepare_token()
    await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 0, 1, 1, {})
    _, response = await client.delete(
        Urls.model_version.format('model_id', run['_id']),
        headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Model not found" in response.text


@pytest.mark.asyncio
async def test_versions_by_task(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    task_id = tasks[0]['_id']
    run = await prepare_run(task_id,  0, 1, 1, {})
    run2 = await prepare_run(task_id, 0, 1, 1, {})
    run3 = await prepare_run(task_id, 0, 1, 1, {})
    model = await prepare_model(TOKEN1)
    model_version = await prepare_model_version(
        model['_id'], run['_id'], created_at=1)
    await prepare_model_version(model['_id'], run2['_id'], deleted_at=1)
    model_version2 = await prepare_model_version(
        model['_id'], run3['_id'], created_at=2)
    _, response = await client.get(
        Urls.task_model_version.format(task_id),
        headers={"x-api-key": TOKEN1})
    model_version.pop('run_id', None)
    model_version.pop('model_id', None)
    model_version['model'] = model
    model_version['run'] = {
        'name': run['name'],
        'number': run['number'],
        '_id': run['_id'],
    }
    assert response.status == 200
    assert response.json[1] == model_version
    assert response.json[0]['_id'] == model_version2['_id']


@pytest.mark.asyncio
async def test_versions_by_task_empty(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    task_id = tasks[0]['_id']
    await prepare_run(task_id,  0, 1, 1, {})
    await prepare_model(TOKEN1)
    _, response = await client.get(
        Urls.task_model_version.format(task_id),
        headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 0


@pytest.mark.asyncio
async def test_versions_by_task_not_exists(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(
        Urls.task_model_version.format('app_id'),
        headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 0
