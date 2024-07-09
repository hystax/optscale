import json
import uuid
import pytest
from datetime import datetime, timezone

from arcee.arcee_receiver.tests.base import (
    Urls, TOKEN1, prepare_token, prepare_run, prepare_artifact,
    prepare_tasks
)


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (Urls.artifacts, client.post),
        (Urls.artifacts, client.get),
        (Urls.artifact.format(str(uuid.uuid4())), client.get),
        (Urls.artifact.format(str(uuid.uuid4())), client.patch),
        (Urls.artifact.format(str(uuid.uuid4())), client.delete),
    ]:
        _, response = await method(path, headers={"x-api-key": "wrong"})
        assert response.status == 401
        assert "Token not found" in response.text

        _, response = await method(path)
        assert response.status == 401
        assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_create_artifact(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id', 99, 1, 1, {})
    artifact = {
        "path": "/my/path",
        "name": "my artifact",
        "description": "my artifact",
        "tags": {"key": "value"},
        "run_id": run['_id']
    }
    _, response = await client.post(Urls.artifacts,
                                    data=json.dumps(artifact),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    assert response.json['run']['_id'] == artifact.pop('run_id', None)
    for key, value in artifact.items():
        assert response.json[key] == value


@pytest.mark.asyncio
async def test_create_invalid_run(app):
    client = app.asgi_client
    await prepare_token()
    artifact = {
        "path": "/my/path",
        "name": "my artifact",
        "description": "my artifact",
        "tags": {"key": "value"},
        "run_id": str(uuid.uuid4())
    }
    _, response = await client.post(Urls.artifacts,
                                    data=json.dumps(artifact),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert 'Run not found' in response.text


@pytest.mark.asyncio
async def test_create_required_params(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id', 99, 1, 1, {})
    artifact = {
        "run_id": run['_id'],
        "path": "path/test"
    }
    _, response = await client.post(Urls.artifacts,
                                    data=json.dumps(artifact),
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 201
    assert response.json['token'] == TOKEN1

    client = app.asgi_client
    await prepare_token()
    for param in ['run_id', 'path']:
        params = artifact.copy()
        params.pop(param, None)
        _, response = await client.post(Urls.artifacts,
                                        data=json.dumps(params),
                                        headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Field required' in response.text


@pytest.mark.asyncio
async def test_create_invalid_params_types(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id', 99, 1, 1, {})
    artifact = {
        "run_id": run['_id'],
        "path": "path/test"
    }
    for param in ["description", "name", "path", "run_id"]:
        for value in [1, {"test": 1}, ['test']]:
            params = artifact.copy()
            params[param] = value
            _, response = await client.post(
                Urls.artifacts, data=json.dumps(params),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text

    for value in [1, "test", ['test']]:
        params = artifact.copy()
        params['tags'] = value
        _, response = await client.post(
            Urls.artifacts, data=json.dumps(params),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid dictionary" in response.text


@pytest.mark.asyncio
async def test_create_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id', 99, 1, 1, {})
    artifact = {
        "run_id": run['_id'],
        "path": "path/test"
    }

    for param in ['_id', 'created_at', 'token', 'test']:
        data = artifact.copy()
        data[param] = 'test'
        _, response = await client.post(Urls.artifacts,
                                        data=json.dumps(data),
                                        headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_list_artifacts_empty(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.artifacts,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 0
    assert response.json['total_count'] == 0
    assert response.json['limit'] == 0
    assert response.json['start_from'] == 0


@pytest.mark.asyncio
async def test_list_invalid_query_params(app):
    client = app.asgi_client
    await prepare_token()
    for param in ['created_at_lt', 'created_at_gt', 'limit', 'start_from']:
        query_url = f'?{param}=test'
        _, response = await client.get(Urls.artifacts + query_url,
                                       headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Input should be a valid integer' in response.text

        query_url = f'?{param}=-10'
        _, response = await client.get(Urls.artifacts + query_url,
                                       headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Input should be greater than or equal to 0' in response.text

    query_url = '?created_at_lt=0&created_at_gt=2'
    _, response = await client.get(Urls.artifacts + query_url,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert 'Invalid created_at filter values' in response.text


@pytest.mark.asyncio
async def test_list_created_at_filter(app):
    client = app.asgi_client
    await prepare_token()
    for param in ['created_at_gt', 'created_at_lt']:
        query_url = f'?{param}={2**32}'
        _, response = await client.get(Urls.artifacts + query_url,
                                       headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert 'Input should be less than or equal ' \
               'to 2147483647' in response.text

        query_url = f'?{param}={2**30}'
        _, response = await client.get(Urls.artifacts + query_url,
                                       headers={"x-api-key": TOKEN1})
        assert response.status == 200


@pytest.mark.asyncio
async def test_list_limit_filter(app):
    client = app.asgi_client
    await prepare_token()
    query_url = f'?limit={2**64}'
    _, response = await client.get(Urls.artifacts + query_url,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert 'Input should be less than or equal ' \
           'to 9223372036854775807' in response.text

    query_url = f'?limit={2**62}'
    _, response = await client.get(Urls.artifacts + query_url,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200


@pytest.mark.asyncio
async def test_list_unexpected_query_params(app):
    client = app.asgi_client
    await prepare_token()
    query_url = '?unexpected=1'
    _, response = await client.get(Urls.artifacts + query_url,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200


@pytest.mark.asyncio
async def test_list_run_id(app):
    client = app.asgi_client
    await prepare_token()
    task = await prepare_tasks()
    run = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    run_id = run['_id']
    now_ts = int(datetime.now(tz=timezone.utc).timestamp())
    await prepare_artifact(run['_id'], created_at=now_ts)

    query_url = f'?run_id={run_id}'
    _, response = await client.get(Urls.artifacts + query_url,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 1

    query_url = f'?run_id={run_id}&run_id=run_id'
    _, response = await client.get(Urls.artifacts + query_url,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 1


@pytest.mark.asyncio
async def test_list_artifacts_created_at(app):
    client = app.asgi_client
    await prepare_token()
    task = await prepare_tasks()
    run = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    now_ts = int(datetime.now(tz=timezone.utc).timestamp())
    artifact = await prepare_artifact(run['_id'], created_at=now_ts)
    date1_ts = now_ts - 10
    await prepare_artifact(run['_id'], created_at=date1_ts)
    date2_ts = now_ts + 10
    await prepare_artifact(run['_id'], created_at=date2_ts)
    _, response = await client.get(
        Urls.artifacts + f'?created_at_lt={date2_ts}&created_at_gt={date1_ts}',
        headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 1
    assert response.json['artifacts'][0]['_id'] == artifact['_id']
    assert response.json['total_count'] == 1
    assert response.json['limit'] == 0
    assert response.json['start_from'] == 0


@pytest.mark.asyncio
async def test_list_artifacts_run_id(app):
    client = app.asgi_client
    await prepare_token()
    task = await prepare_tasks()
    run1 = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    run2 = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    run3 = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    artifact1 = await prepare_artifact(run1['_id'])
    artifact2 = await prepare_artifact(run2['_id'])
    await prepare_artifact(run3['_id'])
    _, response = await client.get(
        Urls.artifacts + f'?run_id={run1["_id"]}&run_id={run2["_id"]}',
        headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 2
    assert response.json['total_count'] == 2
    assert response.json['limit'] == 0
    assert response.json['start_from'] == 0
    for artifact in response.json['artifacts']:
        assert artifact['_id'] in [artifact1['_id'], artifact2['_id']]


@pytest.mark.asyncio
async def test_list_artifacts_task_id(app):
    client = app.asgi_client
    await prepare_token()
    task = await prepare_tasks()
    run1 = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    run2 = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    run3 = await prepare_run(task[1]['_id'], 99, 1, 1, {})
    artifact1 = await prepare_artifact(run1['_id'])
    artifact2 = await prepare_artifact(run2['_id'])
    await prepare_artifact(run3['_id'])
    _, response = await client.get(
        Urls.artifacts + f'?task_id={task[0]["_id"]}',
        headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 2
    assert response.json['total_count'] == 2
    assert response.json['limit'] == 0
    assert response.json['start_from'] == 0
    for artifact in response.json['artifacts']:
        assert artifact['_id'] in [artifact1['_id'], artifact2['_id']]
        assert artifact['run']['task_name'] == task[0]['name']


@pytest.mark.asyncio
async def test_list_artifacts_text_like(app):
    client = app.asgi_client
    await prepare_token()
    task = await prepare_tasks()
    run = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    artifact1 = await prepare_artifact(run['_id'], name='test1')
    artifact2 = await prepare_artifact(run['_id'], description='test2')
    artifact3 = await prepare_artifact(run['_id'], tags={'test3': 1})
    artifact4 = await prepare_artifact(run['_id'], tags={'artifact': 'test4'})
    _, response = await client.get(Urls.artifacts + f'?text_like=test1',
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 1
    assert response.json['total_count'] == 1
    assert response.json['limit'] == 0
    assert response.json['start_from'] == 0
    assert response.json['artifacts'][0]['_id'] == artifact1['_id']

    _, response = await client.get(Urls.artifacts + f'?text_like=test2',
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 1
    assert response.json['total_count'] == 1
    assert response.json['limit'] == 0
    assert response.json['start_from'] == 0
    assert response.json['artifacts'][0]['_id'] == artifact2['_id']

    _, response = await client.get(Urls.artifacts + f'?text_like=test3',
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 1
    assert response.json['total_count'] == 1
    assert response.json['limit'] == 0
    assert response.json['start_from'] == 0
    assert response.json['artifacts'][0]['_id'] == artifact3['_id']

    _, response = await client.get(Urls.artifacts + f'?text_like=test4',
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 1
    assert response.json['total_count'] == 1
    assert response.json['limit'] == 0
    assert response.json['start_from'] == 0
    assert response.json['artifacts'][0]['_id'] == artifact4['_id']


@pytest.mark.asyncio
async def test_list_artifacts_limit(app):
    client = app.asgi_client
    await prepare_token()
    task = await prepare_tasks()
    run = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    await prepare_artifact(run['_id'], created_at=1)
    artifact2 = await prepare_artifact(run['_id'], created_at=2)
    artifact3 = await prepare_artifact(run['_id'], created_at=3)
    _, response = await client.get(Urls.artifacts + f'?limit=1',
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 1
    assert response.json['artifacts'][0]['_id'] == artifact3['_id']
    assert response.json['total_count'] == 3
    assert response.json['limit'] == 1
    assert response.json['start_from'] == 0

    _, response = await client.get(Urls.artifacts + f'?limit=1&start_from=1',
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json['artifacts']) == 1
    assert response.json['artifacts'][0]['_id'] == artifact2['_id']
    assert response.json['total_count'] == 3
    assert response.json['limit'] == 1
    assert response.json['start_from'] == 1


@pytest.mark.asyncio
async def test_list_artifacts_total_count(app):
    client = app.asgi_client
    await prepare_token()
    task = await prepare_tasks()
    run = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    await prepare_artifact(run['_id'], created_at=1)
    await prepare_artifact(run['_id'], created_at=2)
    await prepare_artifact(run['_id'], created_at=3)

    _, response = await client.get(Urls.artifacts,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['total_count'] == 3

    _, response = await client.get(Urls.artifacts + f'?limit=1',
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['total_count'] == 3

    _, response = await client.get(Urls.artifacts + f'?start_from=1',
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['total_count'] == 3

    _, response = await client.get(Urls.artifacts + f'?start_from=10',
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['total_count'] == 3


@pytest.mark.asyncio
async def test_patch_empty(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id', 99, 1, 1, {})
    artifact = await prepare_artifact(run['_id'])
    _, response = await client.patch(
        Urls.artifact.format(artifact['_id']),
        data=json.dumps({}),
        headers={"x-api-key": TOKEN1})
    assert response.status == 200


@pytest.mark.asyncio
async def test_patch_invalid_params_types(app):
    client = app.asgi_client
    await prepare_token()
    artifact = await prepare_artifact(TOKEN1)
    for param in ["description", "name", "path"]:
        for value in [1, {"test": 1}, ['test']]:
            updates = {
                param: value
            }
            _, response = await client.patch(
                Urls.artifact.format(artifact['_id']),
                data=json.dumps(updates),
                headers={"x-api-key": TOKEN1})
            assert response.status == 400
            assert "Input should be a valid string" in response.text

    for value in [1, "test", ['test']]:
        updates = {
            "tags": value
        }
        _, response = await client.patch(
            Urls.artifact.format(artifact['_id']),
            data=json.dumps(updates),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Input should be a valid dictionary" in response.text


@pytest.mark.asyncio
async def test_patch_unexpected(app):
    client = app.asgi_client
    await prepare_token()
    artifact = await prepare_artifact(TOKEN1)
    for param in ['_id', 'created_at', 'run_id', 'token', 'test']:
        updates = {param: 'test'}
        _, response = await client.patch(
            Urls.artifact.format(artifact['_id']),
            data=json.dumps(updates),
            headers={"x-api-key": TOKEN1})
        assert response.status == 400
        assert "Extra inputs are not permitted" in response.text


@pytest.mark.asyncio
async def test_patch_artifact(app):
    client = app.asgi_client
    await prepare_token()
    task = await prepare_tasks()
    run = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    artifact = await prepare_artifact(run_id=run['_id'])
    updates = {
        "name": "new",
        "description": "new",
        "tags": {"new": "new"},
    }
    _, response = await client.patch(Urls.artifact.format(artifact['_id']),
                                     data=json.dumps(updates),
                                     headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['run']['_id'] == artifact.pop('run_id', None)
    for key, value in updates.items():
        assert response.json[key] == value


@pytest.mark.asyncio
async def test_patch_artifact_empty_path(app):
    client = app.asgi_client
    await prepare_token()
    task = await prepare_tasks()
    run = await prepare_run(task[0]['_id'], 99, 1, 1, {})
    artifact = await prepare_artifact(run_id=run['_id'])
    updates = {
        "path": None
    }
    _, response = await client.patch(Urls.artifact.format(artifact['_id']),
                                     data=json.dumps(updates),
                                     headers={"x-api-key": TOKEN1})
    assert response.status == 400
    assert 'Input should be a valid string' in response.text


@pytest.mark.asyncio
async def test_patch_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    updates = {
        "name": "my artifact"
    }
    _, response = await client.patch(Urls.artifact.format('artifact_id'),
                                     data=json.dumps(updates),
                                     headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Artifact not found" in response.text


@pytest.mark.asyncio
async def test_get_artifact(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id', 99, 1, 1, {})
    artifact = await prepare_artifact(run['_id'])
    _, response = await client.get(Urls.artifact.format(artifact['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json['token'] == TOKEN1


@pytest.mark.asyncio
async def test_get_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.artifact.format('artifact_id'),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Artifact not found" in response.text


@pytest.mark.asyncio
async def test_delete_artifact(app):
    client = app.asgi_client
    await prepare_token()
    run = await prepare_run('task_id', 99, 1, 1, {})
    artifact = await prepare_artifact(run['_id'])
    _, response = await client.delete(Urls.artifact.format(artifact['_id']),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 204


@pytest.mark.asyncio
async def test_delete_not_existing(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.delete(Urls.artifact.format('artifact_id'),
                                      headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Artifact not found" in response.text
