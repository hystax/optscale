import json
import uuid
import pytest
from arcee.arcee_receiver.tests.base import (
    DB_MOCK, TOKEN1, Urls, prepare_metrics, prepare_token)


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (Urls.metrics, client.post),
        (Urls.metrics, client.get),
        (Urls.metric.format(str(uuid.uuid4())), client.patch),
        (Urls.metric.format(str(uuid.uuid4())), client.get),
        (Urls.metric.format(str(uuid.uuid4())), client.delete),
    ]:
        _, response = await method(path, headers={"x-api-key": "wrong"})
        assert response.status == 401
        assert "Token not found" in response.text

        _, response = await method(path)
        assert response.status == 401
        assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_create_metric(app):
    client = app.asgi_client
    await prepare_token()
    metric = {
        'key': 'key',
        'name': 'name',
        'tendency': 'less',
        'target_value': 0,
        'func': 'max'
    }
    _, response = await client.post(Urls.metrics,
                                    data=json.dumps(metric),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 200
    for key, value in metric.items():
        assert response.json[key] == value
    assert response.json['token'] == TOKEN1

    _, response = await client.post(Urls.metrics,
                                    data=json.dumps(metric),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 409
    assert "Conflict" in response.text


@pytest.mark.asyncio
async def test_create_metric_missing_param(app):
    client = app.asgi_client
    await prepare_token()
    metric = {
        'key': 'key',
        'tendency': 'less',
        'func': 'avg',
        'target_value': 0
    }
    for param in metric:
        params = metric.copy()
        params.pop(param, None)
        _, response = await client.post(Urls.metrics,
                                        data=json.dumps(params),
                                        headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Field required' in response.text


@pytest.mark.asyncio
async def test_create_metric_invalid_param(app):
    client = app.asgi_client
    await prepare_token()
    metric = {
        'key': 'key',
        'name': 'name',
        'tendency': 'less',
        'func': 'avg',
        'target_value': 0
    }
    for param in ['key', 'name', 'tendency', 'func']:
        for value in [33, ['value'], {'value': 'value'}]:
            params = metric.copy()
            params[param] = value
            _, response = await client.post(Urls.metrics,
                                            data=json.dumps(params),
                                            headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert 'Input should be a valid string' in response.text

    for value in ['value', ['value'], {'value': 'value'}]:
        params = metric.copy()
        params['target_value'] = value
        _, response = await client.post(Urls.metrics,
                                        data=json.dumps(params),
                                        headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Input should be a valid number' in response.text

    for param in ['func', 'tendency']:
        params = metric.copy()
        params[param] = 'test'
        _, response = await client.post(Urls.metrics,
                                        data=json.dumps(params),
                                        headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Input should be' in response.text


@pytest.mark.asyncio
async def test_create_metric_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    metric = {
        'key': 'key',
        'name': 'name',
        'tendency': 'less',
        'func': 'avg',
        'target_value': 0,
        'test': 'test'
    }
    _, response = await client.post(Urls.metrics,
                                    data=json.dumps(metric),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert 'Extra inputs are not permitted' in response.text


@pytest.mark.asyncio
async def test_get_metrics(app):
    client = app.asgi_client
    await prepare_token()
    await prepare_metrics()
    _, response = await client.get(Urls.metrics,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 2


@pytest.mark.asyncio
async def test_patch_invalid_metric(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.patch(Urls.metric.format(str(uuid.uuid4())),
                                     headers={"x-api-key": TOKEN1},
                                     data="{}")
    assert response.status == 404
    assert "Metric not found" in response.text


@pytest.mark.asyncio
async def test_patch_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_metrics()
    for param in ['_id', 'token', 'test']:
        data = dict()
        data[param] = 'test'
        _, response = await client.patch(
            Urls.metric.format(tasks[0]['_id']),
            data=json.dumps(data),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_patch_metric(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    metric_update = {
        'key': 'key',
        'name': 'name',
        'tendency': 'less',
        'func': 'avg',
        'target_value': 0
    }
    _, response = await client.patch(Urls.metric.format(metrics[0]['_id']),
                                     headers={"x-api-key": TOKEN1},
                                     data=json.dumps(metric_update))
    assert response.status == 200
    task = await DB_MOCK['metric'].find_one({'_id': metrics[0]['_id']})
    for k, v in metric_update.items():
        assert v == task[k]


@pytest.mark.asyncio
async def test_patch_invalid_params(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    metric = {
        'key': 'key',
        'name': 'name',
        'tendency': 'less',
        'func': 'avg',
        'target_value': 0
    }
    for param in ['key', 'name', 'tendency', 'func']:
        for value in [33, ['value'], {'value': 'value'}]:
            params = metric.copy()
            params[param] = value
            _, response = await client.patch(
                Urls.metric.format(metrics[0]['_id']),
                data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert 'Input should be a valid string' in response.text

    for value in ['value', ['value'], {'value': 'value'}]:
        params = metric.copy()
        params['target_value'] = value
        _, response = await client.patch(Urls.metric.format(metrics[0]['_id']),
                                         data=json.dumps(params),
                                         headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Input should be a valid number' in response.text

    for param in ['func', 'tendency']:
        params = metric.copy()
        params[param] = 'test'
        _, response = await client.patch(Urls.metric.format(metrics[0]['_id']),
                                         data=json.dumps(params),
                                         headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Input should be' in response.text


@pytest.mark.asyncio
async def test_get_metric(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    _, response = await client.get(Urls.metric.format(metrics[0]['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert metrics[0]['key'] == response.json['key']


@pytest.mark.asyncio
async def test_get_missing_metric(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.metric.format('fake'),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Not found" in response.text


@pytest.mark.asyncio
async def test_delete_missing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.delete(Urls.metric.format('fake'),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Not found" in response.text
