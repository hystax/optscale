import json
import uuid
import pytest
from arcee.arcee_receiver.tests.base import (
    Urls, TOKEN1, prepare_token, prepare_run, prepare_tasks
)


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (Urls.collect, client.post)
    ]:
        _, response = await method(path, headers={"x-api-key": "wrong"})
        assert response.status == 401
        assert "Token not found" in response.text

        _, response = await method(path)
        assert response.status == 401
        assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_collect(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})

    data = {
        "project": tasks[0]['_id'],
        "run": run["_id"],
        "data": {
            "loss": 99
        },
        "platform": {
            "platform_type": "aws",
            "instance_id": str(uuid.uuid4()),
            "account_id": str(uuid.uuid4()),
            "local_ip": "1.1.1.1",
            "public_ip": "1.1.1.1",
            "instance_type": "type",
            "instance_region": "region",
            "availability_zone": "zone",
            "instance_lc": "Spot"
        }
    }
    _, response = await client.post(Urls.collect,
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 200
    run_id = response.json['message']['run']
    assert run_id == run['_id']

    _, response = await client.post(Urls.collect,
                                    data=json.dumps(data),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 200
    run_id = response.json['message']['run']
    assert run_id == run['_id']


@pytest.mark.asyncio
async def test_invalid_params(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    data = {
        "project": tasks[0]['_id'],
        "run": run["_id"],
        "data": {
            "loss": 12
        },
        "platform": {
            "platform_type": "aws",
            "instance_id": str(uuid.uuid4()),
            "account_id": str(uuid.uuid4()),
            "local_ip": "1.1.1.1",
            "public_ip": "1.1.1.1",
            "instance_type": "type",
            "instance_region": "region",
            "availability_zone": "zone",
            "instance_lc": "Spot"
        }
    }

    for param in ["project", "run"]:
        for value in [1, {"test": 1}, ['test']]:
            params = data.copy()
            params[param] = value
            _, response = await client.post(
                Urls.collect, data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text

    for param in ["platform"]:
        for value in [1, "test", ['test']]:
            params = data.copy()
            params[param] = value
            _, response = await client.post(
                Urls.collect, data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid dictionary" in response.text


@pytest.mark.asyncio
async def test_data(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    data = {
        "project": tasks[0]['_id'],
        "run": run["_id"],
        "data": {
            "loss": 12
        },
        "platform": {
            "platform_type": "aws",
            "instance_id": str(uuid.uuid4()),
            "account_id": str(uuid.uuid4()),
            "local_ip": "1.1.1.1",
            "public_ip": "1.1.1.1",
            "instance_type": "type",
            "instance_region": "region",
            "availability_zone": "zone",
            "instance_lc": "Spot"
        }
    }
    params = data.copy()
    params['data'] = {}
    _, response = await client.post(
        Urls.collect, data=json.dumps(params), headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['message']['data'] == {}

    params['data'] = {'test': 'test'}
    _, response = await client.post(
        Urls.collect, data=json.dumps(params), headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['message']['data'] == {}


@pytest.mark.asyncio
async def test_invalid_platform(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    data = {
        "project": tasks[0]['_id'],
        "run": run["_id"],
        "data": {
            "loss": 12
        },
        "platform": {
            "platform_type": "aws",
            "instance_id": str(uuid.uuid4()),
            "account_id": str(uuid.uuid4()),
            "local_ip": "1.1.1.1",
            "public_ip": "1.1.1.1",
            "instance_type": "type",
            "instance_region": "region",
            "availability_zone": "zone",
            "instance_lc": "Spot"
        }
    }
    platform_keys = list(data['platform'].keys())
    for param in platform_keys:
        params = data.copy()
        for value in [1, {"test": 1}, ['test']]:
            params['platform'][param] = value
            _, response = await client.post(
                Urls.collect, data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text

    for param in platform_keys:
        params = data.copy()
        params['platform'].pop(param, None)
        _, response = await client.post(
            Urls.collect, data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Field required" in response.text

    params = data.copy()
    params['platform']['instance_lc'] = 'test'
    _, response = await client.post(
        Urls.collect, data=json.dumps(params), headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Field required" in response.text

    params = data.copy()
    params['platform']['platform_type'] = 'test'
    _, response = await client.post(
        Urls.collect, data=json.dumps(params), headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Field required" in response.text

    params = data.copy()
    params['platform']['test'] = 'test'
    _, response = await client.post(
        Urls.collect, data=json.dumps(params), headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert "Field required" in response.text


@pytest.mark.asyncio
async def test_create_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    run = await prepare_run(tasks[0]['_id'], 99, 1, 1, {})
    data = {
        "project": tasks[0]['_id'],
        "run": run["_id"],
        "data": {
            "loss": 12
        },
        "platform": {
            "platform_type": "aws",
            "instance_id": str(uuid.uuid4()),
            "account_id": str(uuid.uuid4()),
            "local_ip": "1.1.1.1",
            "public_ip": "1.1.1.1",
            "instance_type": "type",
            "instance_region": "region",
            "availability_zone": "zone",
            "instance_lc": "Spot"
        }
    }
    for param in ['_id', 'timestamp', 'test']:
        params = data.copy()
        params[param] = 'test'
        _, response = await client.post(
            Urls.collect, data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text
