import json
import uuid
import pytest
from datetime import datetime, timezone

from arcee.arcee_receiver.tests.base import (
    DB_MOCK, Urls, TOKEN1, prepare_token, prepare_run, prepare_dataset
)


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (Urls.datasets, client.post),
        (Urls.dataset_register, client.post),
        (Urls.datasets, client.get),
        (Urls.dataset.format(str(uuid.uuid4())), client.get),
        (Urls.dataset.format(str(uuid.uuid4())), client.patch),
        (Urls.dataset.format(str(uuid.uuid4())), client.delete),
    ]:
        _, response = await method(path, headers={"x-api-key": "wrong"})
        assert response.status == 401
        assert "Token not found" in response.text

        _, response = await method(path)
        assert response.status == 401
        assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_create_dataset(app):
    client = app.asgi_client
    await prepare_token()
    dataset = {
        "path": "/my/path",
        "name": "my dataset",
        "description": "my dataset",
        "labels": ["test"],
        "timespan_from": 0,
        "timespan_to": 10000
    }
    _, response = await client.post(Urls.datasets,
                                    data=json.dumps(dataset),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    for key, value in dataset.items():
        assert response.json[key] == value


@pytest.mark.asyncio
async def test_create_dataset_conflict(app):
    client = app.asgi_client
    await prepare_token()
    await prepare_dataset(path='test')
    dataset = {
        "path": "test",
        "name": "my dataset",
        "description": "my dataset",
        "labels": ["test"],
        "timespan_from": 0,
        "timespan_to": 10000
    }
    _, response = await client.post(Urls.datasets,
                                    data=json.dumps(dataset),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 409
    assert 'Dataset exists' in response.text


@pytest.mark.asyncio
async def test_register_dataset(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task', 1, 1, 1, {})
    dataset = {
        "path": "/my/path",
        "name": "my dataset",
        "description": "my dataset",
        "labels": ["test"],
        "timespan_from": 0,
        "timespan_to": 10000
    }
    _, response = await client.post(Urls.dataset_register.format(run['_id']),
                                    data=json.dumps(dataset),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 200
    dataset_id = response.json['id']

    _, response = await client.post(Urls.dataset_register.format(run['_id']),
                                    data=json.dumps(dataset),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert dataset_id == response.json['id']


@pytest.mark.asyncio
async def test_register_dataset_invalid_run(app):
    client = app.asgi_client
    await prepare_token()
    dataset = {
        "path": "/my/path",
        "name": "my dataset",
        "description": "my dataset",
        "labels": ["test"],
        "timespan_from": 0,
        "timespan_to": 10000
    }
    _, response = await client.post(Urls.dataset_register.format('test'),
                                    data=json.dumps(dataset),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Run not found" in response.text


@pytest.mark.asyncio
async def test_create_required_params(app):
    client = app.asgi_client
    await prepare_token()
    dataset = {
        "path": "path/test"
    }
    _, response = await client.post(Urls.datasets,
                                    data=json.dumps(dataset),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    assert response.json['token'] == TOKEN1

    _, response = await client.post(Urls.datasets,
                                    data=json.dumps({}),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert 'Field required' in response.text


@pytest.mark.asyncio
async def test_register_required_params(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id')
    dataset = {
        "path": "path/test"
    }
    _, response = await client.post(Urls.dataset_register.format(run['_id']),
                                    data=json.dumps(dataset),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert 'id' in response.text

    _, response = await client.post(Urls.dataset_register.format(run['_id']),
                                    data=json.dumps({}),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert 'Field required' in response.text


@pytest.mark.asyncio
async def test_register_with_none_labels(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id')
    dataset = {
        "path": "path/test",
        "labels": None
    }
    _, response = await client.post(Urls.dataset_register.format(run['_id']),
                                    data=json.dumps(dataset),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert 'id' in response.text


@pytest.mark.asyncio
async def test_create_with_duplicated_labels(app):
    client = app.asgi_client
    await prepare_token()
    dataset = {
        "path": "path/test",
        "labels": ["test", "test"]
    }
    _, response = await client.post(Urls.datasets,
                                    data=json.dumps(dataset),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    assert response.json['labels'] == ["test"]


@pytest.mark.asyncio
async def test_create_invalid_params_types(app):
    client = app.asgi_client
    await prepare_token()
    dataset = {
        "path": "path/test"
    }
    for param in ["description", "name", "path"]:
        for value in [1, {"test": 1}, ['test']]:
            params = dataset.copy()
            params[param] = value
            _, response = await client.post(
                Urls.datasets, data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text

    for param in ["timespan_from", "timespan_to"]:
        for value in ["test", {"test": 1}, ['test']]:
            params = dataset.copy()
            params[param] = value
            _, response = await client.post(
                Urls.datasets, data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid integer" in response.text

    for value in [1, "test", {'test': 'test'}]:
        params = dataset.copy()
        params['labels'] = value
        _, response = await client.post(
            Urls.datasets, data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid list" in response.text


@pytest.mark.asyncio
async def test_register_invalid_params_types(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id')
    dataset = {
        "path": "path/test"
    }
    for param in ["description", "name", "path"]:
        for value in [1, {"test": 1}, ['test']]:
            params = dataset.copy()
            params[param] = value
            _, response = await client.post(
                Urls.dataset_register.format(run['_id']),
                data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text

    for param in ["timespan_from", "timespan_to"]:
        for value in ["test", {"test": 1}, ['test']]:
            params = dataset.copy()
            params[param] = value
            _, response = await client.post(
                Urls.dataset_register.format(run['_id']),
                data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid integer" in response.text

    for value in [1, "test", {'test': 'test'}]:
        params = dataset.copy()
        params['labels'] = value
        _, response = await client.post(
            Urls.dataset_register.format(run['_id']),
            data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid list" in response.text


@pytest.mark.asyncio
async def test_list_datasets_empty(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.datasets,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 0


@pytest.mark.asyncio
async def test_list_datasets(app):
    client = app.asgi_client
    await prepare_token()
    await prepare_dataset()
    _, response = await client.get(Urls.datasets,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 1


@pytest.mark.asyncio
async def test_list_datasets_include_deleted(app):
    client = app.asgi_client
    await prepare_token()
    dataset = {
        "_id": str(uuid.uuid4()),
        "name": 'test',
        "description": 'test',
        "labels": [],
        "path": 'test',
        "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
        "token": TOKEN1,
        "deleted_at": int(datetime.now(tz=timezone.utc).timestamp())
    }
    await DB_MOCK['dataset'].insert_one(dataset)
    _, response = await client.get(Urls.datasets,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 0

    _, response = await client.get(Urls.datasets + '?include_deleted=true',
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 1


@pytest.mark.asyncio
async def test_patch_empty(app):
    client = app.asgi_client
    await prepare_token()
    dataset = await prepare_dataset()
    _, response = await client.patch(
        Urls.dataset.format(dataset['_id']),
        data=json.dumps({}),
        headers={"x-api-key": TOKEN1})
    assert response.status == 200


@pytest.mark.asyncio
async def test_patch_invalid_params_types(app):
    client = app.asgi_client
    await prepare_token()
    dataset = await prepare_dataset()
    body = {
        "path": "path/test"
    }
    for param in ["description", "name"]:
        for value in [1, {"test": 1}, ['test']]:
            params = body.copy()
            params[param] = value
            _, response = await client.patch(
                Urls.dataset.format(dataset['_id']), data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text

    for param in ["timespan_from", "timespan_to"]:
        for value in ["test", {"test": 1}, ['test']]:
            params = body.copy()
            params[param] = value
            _, response = await client.patch(
                Urls.dataset.format(dataset['_id']), data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid integer" in response.text

    for value in [1, "test", {'test': 'test'}]:
        params = body.copy()
        params['labels'] = value
        _, response = await client.patch(
            Urls.dataset.format(dataset['_id']), data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid list" in response.text


@pytest.mark.asyncio
async def test_patch_dataset(app):
    client = app.asgi_client
    await prepare_token()
    dataset = await prepare_dataset()
    updates = {
        "name": "new",
        "description": "new"
    }
    _, response = await client.patch(Urls.dataset.format(dataset['_id']),
                                     data=json.dumps(updates),
                                     headers={"x-api-key": TOKEN1})
    assert response.status == 200
    for key, value in updates.items():
        assert response.json[key] == value


@pytest.mark.asyncio
async def test_patch_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    updates = {
        "name": "my dataset"
    }
    _, response = await client.patch(Urls.dataset.format('dataset_id'),
                                     data=json.dumps(updates),
                                     headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Dataset not found" in response.text


@pytest.mark.asyncio
async def test_get_dataset(app):
    client = app.asgi_client
    await prepare_token()
    dataset = await prepare_dataset()
    _, response = await client.get(Urls.dataset.format(dataset['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['path'] == dataset['path']


@pytest.mark.asyncio
async def test_get_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.dataset.format('dataset_id'),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Dataset not found" in response.text


@pytest.mark.asyncio
async def test_delete_dataset(app, mock_dataset):
    client = app.asgi_client
    await prepare_token()
    dataset = await prepare_dataset()
    _, response = await client.delete(Urls.dataset.format(dataset['_id']),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 204


@pytest.mark.asyncio
async def test_delete_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.delete(Urls.dataset.format('dataset_id'),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Dataset not found" in response.text
