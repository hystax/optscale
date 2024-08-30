import uuid
import pytest

from arcee.arcee_receiver.tests.base import (
    Urls, TOKEN1, prepare_token, prepare_tasks, prepare_run
)


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    _, response = await client.get(Urls.tags.format(str(uuid.uuid4())),
                                   headers={"x-api-key": "wrong"})
    assert response.status == 401
    assert "Token not found" in response.text

    _, response = await client.get(Urls.tags.format(str(uuid.uuid4())))
    assert response.status == 401
    assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_list_tags_empty(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    await prepare_run(tasks[0]['_id'])
    _, response = await client.get(Urls.tags.format(tasks[0]['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 0


@pytest.mark.asyncio
async def test_list_tags(app):
    client = app.asgi_client
    await prepare_token()
    tasks = await prepare_tasks()
    await prepare_run(tasks[0]['_id'], tags={'tag1': 1, 'tag2': 2})
    await prepare_run(tasks[0]['_id'], tags={'tag2': 2})
    await prepare_run(tasks[0]['_id'])
    await prepare_run(tasks[1]['_id'], tags={'tag3': 3})
    _, response = await client.get(Urls.tags.format(tasks[0]['_id']),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json == ["tag1", "tag2"]


@pytest.mark.asyncio
async def test_list_tags_invalid_task(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.tags.format(str(uuid.uuid4())),
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Task not found" in response.text
