import asyncio
import logging
import os
import time

from tornado.gen import multi
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import (Application, HTTPError as ResponseHttpError,
                         RequestHandler, StaticFileHandler)

from async_lru import alru_cache
from requests.exceptions import HTTPError
from typing import Any, Dict
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestApiClient

from diproxy.diproxy.storage_client import RemoteWriteStorageClient

BASEDIR_NAME = os.path.dirname(__file__)
BASEDIR_PATH = os.path.abspath(BASEDIR_NAME)
SWAGGER_PATH = os.path.join(BASEDIR_PATH, 'swagger')

CA_CACHE_SECONDS = 60
DEFAULT_DEBUG_ENABLED = os.environ.get('DEBUG', False)
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80
DEFAULT_PORT = 8935
ETCD_HOST = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
ETCD_PORT = int(os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT))
LOG = logging.getLogger(__name__)
URL_PREFIX = 'storage'

define('etcd_host', default=ETCD_HOST, help='etcd host', type=str)
define('etcd_port', default=ETCD_PORT, help='etcd port', type=int)
define('port', default=DEFAULT_PORT, help='server port', type=int)
define('debug', default=DEFAULT_DEBUG_ENABLED,
       help='enable debug logging', type=bool)


@alru_cache
async def get_cloud_account(rest_cl: RestApiClient, cloud_account_id: str,
                            ttl_hash: float) -> Dict:
    _, cloud_account = await IOLoop.current().run_in_executor(
        None, rest_cl.cloud_account_get, cloud_account_id)
    return cloud_account


def get_ttl_hash(seconds=3600):
    return time.time() // seconds


class Urls:
    write = r"/%s/api/v2/write" % URL_PREFIX
    swagger = r'/%s/swagger/(.*)' % URL_PREFIX


class SwaggerStaticFileHandler(StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, '
                                         'must-revalidate, max-age=0')


class DefaultHandler(RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_status(404)
        self.finish()

    def clear(self) -> None:
        super().clear()
        # not interested in default text/html
        self._headers.pop('Content-Type', None)


class ProxyHandler(RequestHandler):
    _CLOUD_ACCOUNT_ID_KEY = 'Cloud-Account-Id'
    _AUTHORIZATION_KEY = 'Authorization'

    def initialize(self, rest_cl: RestApiClient,
                   storage_cl: RemoteWriteStorageClient) -> None:
        self.rest_cl = rest_cl
        self.storage_cl = storage_cl
        super().initialize()

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        self.finish()

    def clear(self) -> None:
        super().clear()
        # not interested in default text/html
        self._headers.pop('Content-Type', None)

    async def post(self) -> None:
        """
        ---
        tags: [proxy]
        summary: Proxy request to storage
        description: >
            Proxies request to storage and returns storage response as is
        consumes:
        - application/protobuf
        parameters:
        -   in: body
            name: body
            description: Request payload which will be proxied
            required: true
        responses:
            204:
                description: No Content
            400:
                description: |
                    Wrong arguments:
                    - Cloud-Account-Id header not provided
            401:
                description: |
                    Unauthorized:
                    - Authorization header not provided
                    - incorrect credentials in Authorization header
            422:
                description: |
                    Unprocessable Entity:
                    - No cloud account found by provided id
                    - Cloud account deleted
                    - Incorrect cloud account type
            503:
                description: |
                    Service Unavailable:
                    - Storage write failed
        security:
        - basicAuth: []
        """
        cloud_account_id = self.request.headers.get(
            self._CLOUD_ACCOUNT_ID_KEY)
        if cloud_account_id is None:
            LOG.debug('Unknown request')
            raise ResponseHttpError(400)
        try:
            cloud_account = await get_cloud_account(
                self.rest_cl, cloud_account_id,
                get_ttl_hash(CA_CACHE_SECONDS))
        except HTTPError as ex:
            LOG.warning('Failed to get cloud account - %s', str(ex))
            raise ResponseHttpError(422)

        credentials = cloud_account.get('config', {}).get('credentials')
        if not credentials:
            LOG.warning('Unprocessable request to cloud_account_id %s',
                        cloud_account_id)
            raise ResponseHttpError(422)

        authorization = self.request.headers.get(self._AUTHORIZATION_KEY)
        if authorization != f'Basic {credentials}':
            self.set_header('Www-Authenticate', 'Basic')
            LOG.warning('Unauthorized request for cloud_account_id %s',
                        cloud_account_id)
            raise ResponseHttpError(401)
        try:
            code, data, headers = await self.storage_cl.write(
                self.request.headers, self.request.body)
            LOG.debug('Storage write result %s', code)
        except Exception as ex:
            LOG.exception(ex)
            raise ResponseHttpError(503)

        self.clear()
        self.write(data)
        for k, v in headers.items():
            self.set_header(k, v)
        self.set_status(code)


async def get_restapi_client(config_cl: ConfigClient) -> RestApiClient:
    rest_url = await IOLoop.current().run_in_executor(
        None, config_cl.restapi_url)
    cluster_secret = await IOLoop.current().run_in_executor(
        None, config_cl.cluster_secret)
    return RestApiClient(url=rest_url, secret=cluster_secret,
                         verify=not options.debug)


async def get_storage_client(
        config_cl: ConfigClient) -> RemoteWriteStorageClient:
    thanos_url = await IOLoop.current().run_in_executor(
        None, config_cl.thanos_remote_write_url)
    return RemoteWriteStorageClient(thanos_url, verify=not options.debug)


def get_handlers(handler_kwargs):
    return [
        (Urls.write, ProxyHandler, handler_kwargs),
    ]


async def make_app() -> Application:
    config_cl = ConfigClient(host=options.etcd_host, port=options.etcd_port)
    rest_cl, storage_cl = await multi([
        get_restapi_client(config_cl),
        get_storage_client(config_cl)])
    handler_kwargs = {
        'storage_cl': storage_cl,
        'rest_cl': rest_cl,
    }
    return Application(
        get_handlers(handler_kwargs) +
        [(Urls.swagger, SwaggerStaticFileHandler,
          {'path': SWAGGER_PATH, 'default_filename': 'index.html'})],
        default_handler_class=DefaultHandler,
        debug=options.debug
    )


async def main() -> None:
    parse_command_line()
    log_level = logging.INFO
    if options.debug:
        LOG.info('Enabling debug logging')
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, force=True)

    app = await make_app()
    LOG.info("Start listening on port %d", options.port)
    app.listen(options.port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
