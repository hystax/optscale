import requests

from tools.cloud_adapter.lib.azure_partner.decorators import (
    _wrap_http_errors, _wrap_connection_errors)
from tools.cloud_adapter.lib.azure_partner.exceptions import (
    AzurePartnerAuthException, AzurePartnerApiException,
    AzurePartnerConnectionException)


class AzurePartnerClient:
    AUTH_URL = 'https://login.microsoftonline.com/{}/oauth2/token'
    BASE_URL = 'https://api.partnercenter.microsoft.com/v1'
    TOKEN_REFRESH_ATTEMPTS = 1
    CONNECTION_TIMEOUT_SECONDS = 300

    def __init__(self, tenant_id, client_id, client_secret):
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = None

    @property
    def token(self):
        if not self._token:
            self.refresh_token()
        return self._token

    @_wrap_connection_errors(AzurePartnerConnectionException)
    @_wrap_http_errors(AzurePartnerAuthException)
    def refresh_token(self):
        result = requests.post(
            self.AUTH_URL.format(self._tenant_id),
            data={
                'resource': 'https://graph.windows.net',
                'client_id': self._client_id,
                'client_secret': self._client_secret,
                'grant_type': 'client_credentials',
            },
            timeout=self.CONNECTION_TIMEOUT_SECONDS,
        )
        result.raise_for_status()
        self._token = result.json()['access_token']

    @_wrap_connection_errors(AzurePartnerConnectionException)
    @_wrap_http_errors(AzurePartnerApiException)
    def request(self, method, url, params=None, data=None, json=None,
                headers=None):
        if not headers:
            headers = {}
        result = None
        for i in range(self.TOKEN_REFRESH_ATTEMPTS + 1):
            headers['Authorization'] = f'Bearer {self.token}'
            result = requests.request(
                method=method,
                url=f'{self.BASE_URL}/{url}',
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=self.CONNECTION_TIMEOUT_SECONDS,
            )
            if i < self.TOKEN_REFRESH_ATTEMPTS and result.status_code == 401:
                self.refresh_token()
                continue
            break

        result.raise_for_status()
        if result.status_code != 204:
            return result.json()

    def __getattr__(self, attr):
        return lambda value=None: _AzurePartnerRequestBuilder(
            client=self,
            url=attr + (f'/{value}' if value else ''),
        )


class _AzurePartnerRequestBuilder:
    HTTP_METHODS = ['get', 'options', 'head', 'post', 'put', 'patch', 'delete']

    def __init__(self, client, url):
        self._client = client
        self._url = url

    def get_paged(self, **kwargs):
        result = self.get(**kwargs)
        if result:
            for item in result['items']:
                yield item
            while result.get('links', {}).get('next'):
                next_link = result['links']['next']
                result = self._client.request(
                    method=next_link['method'].lower(),
                    url=next_link['uri'],
                    headers={h['key']: h['value']
                             for h in next_link['headers']}
                )
                for item in result['items']:
                    yield item

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
