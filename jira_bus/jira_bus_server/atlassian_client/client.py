"""
Atlassian RestAPI Client

I could not find a Jira client library that can use shared secret credentials,
so here is a simple client implemented from scratch.

This client is dynamic: it uses method chaining to construct URLs and fetch
results. Methods that match HTTP method names will perform request and are
expected to be the last method in chain. All other methods are used for URL
string construction: method name becomes an URL part and optional string
parameter also becomes an URL part.

Example: atlassian_client.issue('OSB-2491').get(fields='status')
This will be a GET request to /rest/api/3/issue/OSB-2491?fields=status
"""

import logging
from datetime import datetime
from urllib.parse import urlencode

import jwt
import requests
from atlassian_jwt.url_utils import hash_url

from jira_bus_server.atlassian_client.decorators import _wrap_request_errors
from jira_bus_server.atlassian_client.exceptions import (
    AtlassianClientException)

LOG = logging.getLogger(__name__)


class AtlassianClient:
    CONNECTION_TIMEOUT_SECONDS = 300
    TOKEN_EXPIRE_SECONDS = 300
    API_PREFIX = 'rest/api/3'

    def __init__(self, app_key, base_url, shared_secret):
        self.app_key = app_key
        self.base_url = base_url
        self.shared_secret = shared_secret

    def _create_token(self, method, relative_url):
        now_timestamp = int(datetime.utcnow().timestamp())
        return jwt.encode(
            payload={
                'iss': self.app_key,
                'iat': now_timestamp,
                'exp': now_timestamp + self.TOKEN_EXPIRE_SECONDS,
                'qsh': hash_url(method, relative_url),
            },
            key=self.shared_secret,
            algorithm='HS256',
        ).decode()

    @_wrap_request_errors(AtlassianClientException)
    def request(self, method, url, params=None, data=None, json=None,
                headers=None):
        if not headers:
            headers = {}
        relative_url = f'{self.API_PREFIX}/{url}?{urlencode(params)}'
        headers['Accept'] = 'application/json'
        headers['Authorization'] = 'JWT {}'.format(
            self._create_token(method, relative_url))
        result = requests.request(
            method=method,
            url=f'{self.base_url}/{relative_url}',
            headers=headers,
            data=data,
            json=json,
            timeout=self.CONNECTION_TIMEOUT_SECONDS,
        )
        result.raise_for_status()
        if result.status_code != 204:
            return result.json()

    def __getattr__(self, attr):
        return lambda value=None: _AtlassianClientRequestBuilder(
            client=self,
            url=attr + (f'/{value}' if value else ''),
        )


class _AtlassianClientRequestBuilder:
    HTTP_METHODS = ['get', 'options', 'head', 'post', 'put', 'patch', 'delete']

    def __init__(self, client, url):
        self._client = client
        self._url = url

    def __getattr__(self, attr):
        if attr in self.HTTP_METHODS:
            return (
                lambda r_data=None, r_json=None, **kwargs:
                self._client.request(
                    method=attr,
                    url=self._url,
                    params=kwargs,
                    data=r_data,
                    json=r_json,
                ))
        else:
            return lambda value=None: self.__class__(
                client=self._client,
                url=f'{self._url}/{attr}' + (f'/{value}' if value else ''),
            )
