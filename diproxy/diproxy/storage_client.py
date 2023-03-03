from typing import Dict, Optional, Union

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import HTTPHeaders


class RemoteWriteStorageClient:
    def __init__(
            self, url: str, method: Optional[str] = 'POST',
            verify: Optional[bool] = True) -> None:
        self.method = method
        self.verify = verify
        self.url = url
        self.client = AsyncHTTPClient()

    async def write(
            self, headers: Union[Dict[str, str], HTTPHeaders],
            body: Union[bytes, str]
    ) -> tuple[int, bytes, HTTPHeaders]:
        request = HTTPRequest(
            method=self.method,
            url=self.url,
            headers=headers,
            body=body,
            validate_cert=self.verify
        )
        response = await self.client.fetch(request, raise_error=False)
        return response.code, response.body, response.headers
