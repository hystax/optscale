import json
import uuid
import pytest
from arcee.arcee_receiver.tests.base import (
    DB_MOCK, Urls, TOKEN1, prepare_token, prepare_run, prepare_model,
    prepare_model_version
)


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (Urls.models, client.post),
        (Urls.models, client.get),
        (Urls.model.format(str(uuid.uuid4())), client.get),
        (Urls.model.format(str(uuid.uuid4())), client.patch),
        (Urls.model.format(str(uuid.uuid4())), client.delete),
    ]:
        _, response = await method(path, headers={"x-api-key": "wrong"})
        assert response.status == 401
        assert "Token not found" in response.text

        _, response = await method(path)
        assert response.status == 401
        assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_create_model(app):
    client = app.asgi_client
    await prepare_token()
    model = {
        "key": "key",
        "name": "my model",
        "description": "my model",
        "tags": {"key": "value"},
    }
    _, response = await client.post(Urls.models,
                                    data=json.dumps(model),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    for key, value in model.items():
        assert response.json[key] == value
    assert response.json['token'] == TOKEN1


@pytest.mark.asyncio
async def test_find_existing_model_on_create(app):
    client = app.asgi_client
    await prepare_token()
    model = {
        "key": "key"
    }
    await prepare_model(TOKEN1)
    _, response = await client.post(Urls.models,
                                    data=json.dumps(model),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    for key, value in model.items():
        assert response.json[key] == value
    assert response.json['token'] == TOKEN1
    count = await DB_MOCK['model'].count_documents({'token': TOKEN1})
    assert count == 1


@pytest.mark.asyncio
async def test_create_required_params(app):
    client = app.asgi_client
    await prepare_token()
    model = {
        "key": "key",
    }
    _, response = await client.post(Urls.models,
                                    data=json.dumps(model),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    for key, value in model.items():
        assert response.json[key] == value
    assert response.json['token'] == TOKEN1

    client = app.asgi_client
    await prepare_token()
    model = {}
    _, response = await client.post(Urls.models,
                                    data=json.dumps(model),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert 'Field required' in response.text


@pytest.mark.asyncio
async def test_create_invalid_key(app):
    client = app.asgi_client
    await prepare_token()
    for key in [1, None, {"test": 1}, ['test']]:
        model = {
            "key": key
        }
        _, response = await client.post(Urls.models,
                                        data=json.dumps(model),
                                        headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid string" in response.text


@pytest.mark.asyncio
async def test_create_without_key(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.post(Urls.models,
                                    data=json.dumps({}),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Field required" in response.text


@pytest.mark.asyncio
async def test_create_without_name(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.post(Urls.models,
                                    data=json.dumps({'key': 'key'}),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    assert response.json['name'] == 'key'


@pytest.mark.asyncio
async def test_create_invalid_params_types(app):
    client = app.asgi_client
    await prepare_token()
    for param in ["description", "name"]:
        for value in [1, {"test": 1}, ['test']]:
            model = {
                "key": "key",
                param: value
            }
            _, response = await client.post(
                Urls.models, data=json.dumps(model),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text

    for value in [1, "test", ['test']]:
        model = {
            "key": "key",
            "tags": value
        }
        _, response = await client.post(
            Urls.models, data=json.dumps(model),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid dictionary" in response.text


@pytest.mark.asyncio
async def test_list_models(app):
    client = app.asgi_client
    await prepare_token()
    model1 = await prepare_model(TOKEN1)
    model1_id = model1['_id']
    model2 = await prepare_model(TOKEN1)
    await prepare_model_version(
        model1_id, 'run_id', aliases=['1', '2', '3', '4'], created_at=1)
    model_version2 = await prepare_model_version(
        model1_id, 'run_id2', aliases=['5', '6'], created_at=2)
    _, response = await client.get(Urls.models,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 2
    for resp_model in response.json:
        if resp_model['_id'] == model1_id:
            test_model = model1
            assert resp_model['last_version'] == model_version2
            assert len(resp_model['aliased_versions']) == 6
        else:
            test_model = model2
        for key, value in test_model.items():
            assert resp_model[key] == value


@pytest.mark.asyncio
async def test_list_models_empty(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.models,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 0


@pytest.mark.asyncio
async def test_create_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    model = {
        "key": "key"
    }

    for param in ['_id', 'created_at', 'token', 'test']:
        data = model.copy()
        data[param] = 'test'
        _, response = await client.post(Urls.models,
                                        data=json.dumps(data),
                                        headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_patch_empty(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    _, response = await client.patch(
        Urls.model.format(model['_id']),
        data=json.dumps({}),
        headers={"x-api-key": TOKEN1})
    assert response.status == 200


@pytest.mark.asyncio
async def test_patch_invalid_params_types(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    for param in ["description", "name"]:
        for value in [1, {"test": 1}, ['test']]:
            updates = {
                param: value
            }
            _, response = await client.patch(
                Urls.model.format(model['_id']), data=json.dumps(updates),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text

    for value in [1, "test", ['test']]:
        updates = {
            "tags": value
        }
        _, response = await client.patch(
            Urls.model.format(model['_id']),
            data=json.dumps(updates),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid dictionary" in response.text


@pytest.mark.asyncio
async def test_patch_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    for param in ['_id', 'created_at', 'key', 'token', 'test']:
        updates = {param: 'test'}
        _, response = await client.patch(
            Urls.model.format(model['_id']),
            data=json.dumps(updates),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_patch_model(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    updates = {
        "name": "my model",
        "description": "my model",
        "tags": {"key": "value"},
    }
    _, response = await client.patch(Urls.model.format(model['_id']),
                                     data=json.dumps(updates),
                                     headers={"x-api-key": TOKEN1})
    assert response.status == 200
    for key, value in updates.items():
        assert response.json[key] == value
    assert response.json['token'] == TOKEN1


@pytest.mark.asyncio
async def test_patch_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    updates = {
        "name": "my model"
    }
    _, response = await client.patch(Urls.model.format('model_id'),
                                     data=json.dumps(updates),
                                     headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Model not found" in response.text


@pytest.mark.asyncio
async def test_get_model(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model(TOKEN1)
    run = await prepare_run('task_id', 99, 1, 1, {})
    run2 = await prepare_run('task_id', 99, 1, 1, {})
    version = await prepare_model_version(
        model['_id'], run['_id'], tags={'test': 'test'},
        aliases=['alias1', 'alias2', 'alias3', 'alias4', 'alias5', 'alias6'])
    await prepare_model_version(
        model['_id'], run2['_id'], deleted_at=1, aliases=[])
    _, response = await client.get(Urls.model.format(model['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    for key, value in model.items():
        assert response.json[key] == value
    version = {
        '_id': version['_id'],
        'path': '/my/path',
        'version': '1',
        'run': {
            'task_id': 'task_id',
            'name': 99,
            'number': 1,
            '_id': run['_id']
        },
        'tags': {'test': 'test'},
        'created_at': version['created_at']
    }
    assert len(response.json['versions']) == 1
    for k, v in version.items():
        assert response.json['versions'][0][k] == v
    assert len(response.json['versions'][0]['aliases']) == 6


@pytest.mark.asyncio
async def test_get_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.model.format('model_id'),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Model not found" in response.text


@pytest.mark.asyncio
async def test_delete_model(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model()
    _, response = await client.delete(Urls.model.format(model['_id']),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 204


@pytest.mark.asyncio
async def test_delete_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.delete(Urls.model.format('model_id'),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Model not found" in response.text


@pytest.mark.asyncio
async def test_delete_with_versions(app):
    client = app.asgi_client
    await prepare_token()
    model = await prepare_model()
    await prepare_model_version(model['_id'], 'run_id')
    _, response = await client.delete(Urls.model.format(model['_id']),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 204
    res = await DB_MOCK['model_version'].find_one({'model_id': model['_id']})
    assert res is None
