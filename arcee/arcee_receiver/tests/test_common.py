import pytest
from arcee.arcee_receiver.tests.base import TOKEN1


@pytest.mark.asyncio
async def test_invalid_url(app):
    client = app.asgi_client
    _, response = await client.post('test/test',
                                    headers={"x-api-key": TOKEN1})
    assert response.status == 404
    assert "Not Found" in response.text
