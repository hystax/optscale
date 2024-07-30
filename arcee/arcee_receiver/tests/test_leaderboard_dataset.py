import datetime
import json
import uuid
import pytest
import sys
from arcee.arcee_receiver.tests.base import (
    DB_MOCK, TOKEN1, Urls, prepare_tasks, prepare_metrics, prepare_token,
    prepare_leaderboard, prepare_dataset, prepare_leaderboard_dataset
)


sys.path.append('.')


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (Urls.leaderboard_datasets.format(str(uuid.uuid4())), client.get),
        (Urls.leaderboard_datasets.format(str(uuid.uuid4())), client.post),
        (Urls.leaderboard_dataset.format(str(uuid.uuid4())), client.get),
        (Urls.leaderboard_dataset.format(str(uuid.uuid4())), client.patch),
        (Urls.leaderboard_dataset.format(str(uuid.uuid4())), client.delete),
    ]:
        _, response = await method(path, headers={"x-api-key": "wrong"})
        assert response.status == 401
        assert "Token not found" in response.text

        _, response = await method(path)
        assert response.status == 401
        assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_create_leaderboard_dataset(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks(metrics[0]['_id'])
    lb = await prepare_leaderboard(metrics[0]['_id'], tasks[0]['_id'])
    ds = await prepare_dataset()
    lb_dataset = {
        'name': 'name',
        'dataset_ids': [ds['_id']],
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": ['tag']
    }
    _, response = await client.post(
        Urls.leaderboard_datasets.format(lb['_id']),
        data=json.dumps(lb_dataset),
        headers={"x-api-key": TOKEN1})
    assert response.status == 201
    for key, value in lb_dataset.items():
        assert response.json[key] == value
    assert response.json['deleted_at'] == 0
    assert response.json['token'] == TOKEN1

    _, response2 = await client.post(
        Urls.leaderboard_datasets.format(lb['_id']),
        data=json.dumps(lb_dataset),
        headers={"x-api-key": TOKEN1})
    assert response2.status == 201
    assert response2.json['_id'] != response.json['_id']


@pytest.mark.asyncio
async def test_create_invalid_lb(app):
    client = app.asgi_client
    await prepare_token()
    ds = await prepare_dataset()
    metrics = await prepare_metrics()
    lb_dataset = {
        'name': 'name',
        'dataset_ids': [ds['_id']],
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": ['tag']
    }
    _, response = await client.post(
        Urls.leaderboard_datasets.format('test'),
        data=json.dumps(lb_dataset),
        headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert 'Leaderboard not found' in response.text


@pytest.mark.asyncio
async def test_create_invalid_params(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks(metrics[0]['_id'])
    lb = await prepare_leaderboard(metrics[0]['_id'], tasks[0]['_id'])
    ds = await prepare_dataset()
    lb_dataset = {
        'name': 'name',
        'dataset_ids': [ds['_id']],
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": ['tag']
    }
    for value in [123, [123], {'test': 123}]:
        params = lb_dataset.copy()
        params['name'] = value
        _, response = await client.post(
            Urls.leaderboard_datasets.format(lb['_id']),
            data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'should be a valid string' in response.text

    for value in [123, '123', {'test': 123}]:
        params = lb_dataset.copy()
        params['dataset_ids'] = value
        _, response = await client.post(
            Urls.leaderboard_datasets.format(lb['_id']),
            data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'should be a valid list' in response.text


@pytest.mark.asyncio
async def test_create_missing_params(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks(metrics[0]['_id'])
    lb = await prepare_leaderboard(metrics[0]['_id'], tasks[0]['_id'])
    ds = await prepare_dataset()
    lb_dataset = {
        'name': 'name',
        'dataset_ids': [ds['_id']],
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": ['tag']
    }
    for param in ['name', 'dataset_ids']:
        params = lb_dataset.copy()
        params.pop(param, None)
        _, response = await client.post(
            Urls.leaderboard_datasets.format(lb['_id']),
            data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 201
        assert not response.json[param]


@pytest.mark.asyncio
async def test_list_missing_lb(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.leaderboard_datasets.format('fake'),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert "[]" in response.text


@pytest.mark.asyncio
async def test_get_leaderboard_dataset(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks(metrics[0]['_id'])
    lb = await prepare_leaderboard(metrics[0]['_id'], tasks[0]['_id'])
    lb_dataset = await prepare_leaderboard_dataset(lb['_id'])
    _, response = await client.get(Urls.leaderboard_dataset.format(
        lb_dataset['_id']), headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['_id'] == lb_dataset['_id']


@pytest.mark.asyncio
async def test_patch_invalid_lb_dataset(app):
    client = app.asgi_client
    await prepare_token()
    lb_dataset = {
        'name': 'name'
    }
    _, response = await client.patch(
        Urls.leaderboard_dataset.format('test'),
        data=json.dumps(lb_dataset),
        headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert 'LeaderboardDataset not found' in response.text


@pytest.mark.asyncio
async def test_patch_invalid_params(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks(metrics[0]['_id'])
    lb = await prepare_leaderboard(metrics[0]['_id'], tasks[0]['_id'])
    ds = await prepare_dataset()
    lb_dataset = await prepare_leaderboard_dataset(lb['_id'])
    updates = {
        'name': 'name',
        'dataset_ids': [ds['_id']]
    }
    for value in [123, [123], {'test': 123}]:
        params = updates.copy()
        params['name'] = value
        _, response = await client.patch(
            Urls.leaderboard_dataset.format(lb_dataset['_id']),
            data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'should be a valid string' in response.text

    for value in [123, '123', {'test': 123}]:
        params = updates.copy()
        params['dataset_ids'] = value
        _, response = await client.patch(
            Urls.leaderboard_dataset.format(lb_dataset['_id']),
            data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'should be a valid list' in response.text


@pytest.mark.asyncio
async def test_patch_missing_params(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks(metrics[0]['_id'])
    lb = await prepare_leaderboard(metrics[0]['_id'], tasks[0]['_id'])
    ds = await prepare_dataset()
    lb_dataset = await prepare_leaderboard_dataset(lb['_id'])
    updates = {
        'name': 'name',
        'dataset_ids': [ds['_id']],
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [],
        "filters": [],
        "group_by_hp": True,
        "grouping_tags": [],
    }
    for param in updates.keys():
        params = updates.copy()
        params.pop(param, None)
        _, response = await client.patch(
            Urls.leaderboard_dataset.format(lb_dataset['_id']),
            data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 200


@pytest.mark.asyncio
async def test_patch_leaderboard_dataset(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks(metrics[0]['_id'])
    lb = await prepare_leaderboard(metrics[0]['_id'], tasks[0]['_id'])
    ds = await prepare_dataset()
    lb_dataset = await prepare_leaderboard_dataset(lb['_id'])
    updates = {
        'name': 'name',
        'dataset_ids': [ds['_id']],
        "primary_metric": metrics[0]['_id'],
        "other_metrics": [metrics[1]['_id']],
        "filters": [{"id": metrics[1]['_id'], "min": 0, "max": 100}],
        "group_by_hp": True,
        "grouping_tags": ['tag']
    }
    _, response = await client.patch(
        Urls.leaderboard_dataset.format(lb_dataset['_id']),
        data=json.dumps(updates),
        headers={"x-api-key": TOKEN1})
    assert response.status == 200
    for key, value in updates.items():
        assert response.json[key] == value


@pytest.mark.asyncio
async def test_delete_missing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.delete(Urls.leaderboard_dataset.format('fake'),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "LeaderboardDataset not found" in response.text


@pytest.mark.asyncio
async def test_delete_leaderboard_dataset(app):
    client = app.asgi_client
    await prepare_token()
    metrics = await prepare_metrics()
    tasks = await prepare_tasks(metrics[0]['_id'])
    lb = await prepare_leaderboard(metrics[0]['_id'], tasks[0]['_id'])
    lb_dataset = await prepare_leaderboard_dataset(lb['_id'])
    _, response = await client.delete(
        Urls.leaderboard_dataset.format(lb_dataset['_id']),
        headers={"x-api-key": TOKEN1})
    assert response.status == 204
    result = await DB_MOCK['leaderboard_dataset'].find_one(
        {'_id': lb_dataset['_id']})
    assert result['deleted_at'] != 0
