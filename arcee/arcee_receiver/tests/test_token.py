import uuid
import json
import pytest

from arcee.arcee_receiver.tests.base import (
    Urls, SECRET, prepare_token
)


@pytest.mark.asyncio
async def test_invalid_token(app):
    client = app.asgi_client
    for path, method in [
        (Urls.tokens, client.post),
        (Urls.token.format(str(uuid.uuid4())), client.get),
        (Urls.token.format(str(uuid.uuid4())), client.delete),
    ]:
        _, response = await method(path, headers={"secret": "wrong"})
        assert response.status == 401
        assert "secret is invalid" in response.text

        _, response = await method(path)
        assert response.status == 401
        assert "secret is required" in response.text


@pytest.mark.asyncio
async def test_create_token(app):
    client = app.asgi_client
    token = {'token': 'test'}
    _, response = await client.post(Urls.tokens,
                                    data=json.dumps(token),
                                    headers={"secret": SECRET})
    assert response.status == 200
    assert response.json['token'] == token['token']


@pytest.mark.asyncio
async def test_get_token(app):
    client = app.asgi_client
    tokens = await prepare_token()
    token_id = tokens[0]['_id']
    _, response = await client.get(Urls.token.format(token_id),
                                   headers={"secret": SECRET})
    assert response.status == 200
    assert response.json['_id'] == token_id


@pytest.mark.asyncio
async def test_get_token_invalid(app):
    client = app.asgi_client
    _, response = await client.get(Urls.token.format('token_id'),
                                   headers={"secret": SECRET})
    assert response.status == 404
    assert "Not found" in response.text


@pytest.mark.asyncio
async def test_delete_token(app):
    client = app.asgi_client
    tokens = await prepare_token()
    token_id = tokens[0]['_id']
    _, response = await client.delete(Urls.token.format(token_id),
                                      headers={"secret": SECRET})
    assert response.status == 200


@pytest.mark.asyncio
async def test_delete_token_invalid(app):
    client = app.asgi_client
    _, response = await client.delete(Urls.token.format('token_id'),
                                      headers={"secret": SECRET})
    assert response.status == 404
    assert "Not found" in response.text
