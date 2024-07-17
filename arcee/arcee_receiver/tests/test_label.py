import pytest

from arcee.arcee_receiver.tests.base import (
    Urls, TOKEN1, prepare_token, prepare_dataset
)


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    _, response = await client.get(Urls.labels, headers={"x-api-key": "wrong"})
    assert response.status == 401
    assert "Token not found" in response.text

    _, response = await client.get(Urls.labels)
    assert response.status == 401
    assert "API key is required" in response.text


@pytest.mark.asyncio
async def test_list_labels_empty(app):
    client = app.asgi_client
    await prepare_token()
    _, response = await client.get(Urls.datasets,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert len(response.json) == 0


@pytest.mark.asyncio
async def test_list_labels(app):
    client = app.asgi_client
    await prepare_token()
    await prepare_dataset(labels=["test1", "test2"])
    await prepare_dataset(labels=["test3"])
    _, response = await client.get(Urls.labels,
                                   headers={"x-api-key": TOKEN1})
    assert response.status == 200
    assert response.json == ["test1", "test2", "test3"]
