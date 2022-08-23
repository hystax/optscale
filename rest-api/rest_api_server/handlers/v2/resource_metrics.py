import json
import logging

from datetime import datetime
from tornado.concurrent import run_on_executor

from rest_api_server.controllers.cloud_resource import CloudResourceAsyncController
from rest_api_server.exceptions import Err
from rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.utils import run_task, check_int_attribute

from metroculus_client.client import Client as MetroculusClient
from optscale_exceptions.common_exc import WrongArgumentsException
from optscale_exceptions.http_exc import OptHTTPError

LOG = logging.getLogger(__name__)
DEFAULT_INTERVAL = 900


class ResourceMetricsAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                                      BaseHandler):
    def _get_controller_class(self):
        return CloudResourceAsyncController

    @staticmethod
    def check_date_arguments(args):
        max_date_length = int(datetime.max.timestamp() - 1)
        date_arg_names = ['end_date', 'start_date']

        try:
            for arg_name in date_arg_names:
                check_int_attribute(
                    arg_name, args[arg_name], max_length=max_date_length)
            if args[date_arg_names[0]] - args[date_arg_names[1]] < 0:
                raise WrongArgumentsException(
                    Err.OE0446, date_arg_names)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)

    def get_metric_arguments(self):
        args = {
            'start_date': self.get_arg('start_date', int),
            'end_date': self.get_arg('end_date', int, default=int(datetime.utcnow().timestamp())),
            'interval': self.get_arg('interval', int, default=DEFAULT_INTERVAL)
        }
        for param, value in args.items():
            if value is None:
                raise OptHTTPError(400, Err.OE0216, [param])

        unexpected_args = list(filter(lambda x: x not in list(args.keys()),
                                      self.request.arguments.keys()))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])

        if args['interval'] % DEFAULT_INTERVAL != 0:
            raise OptHTTPError(400, Err.OE0474, ['interval', DEFAULT_INTERVAL])

        self.check_date_arguments(args)
        return args

    @run_on_executor
    def get_metrics(self, cloud_account_id, resource_id,
                    start_date, end_date, interval):
        client = MetroculusClient(url=self._config.metroculus_url(),
                                  secret=self._config.cluster_secret())
        _, result = client.get_metrics(
            cloud_account_id=cloud_account_id, resource_id=resource_id,
            start_date=start_date, end_date=end_date, interval=interval)
        return result

    async def get(self, resource_id):
        """
        ---
        description: |
            Get resource metrics
            Required permission: INFO_ORGANIZATION
        tags: [resource_metrics]
        summary: Get resource metrics
        parameters:
        -   name: resource_id
            in: path
            description: Resource ID
            required: true
            type: string
        -   name: start_date
            in: query
            description: Start date (timestamp in seconds)
            required: true
            type: integer
        -   name: end_date
            in: query
            description: End date (timestamp in seconds)
            required: false
            type: integer
        -   name: interval
            in: query
            description: Interval (must be multiple of 900)
            required: false
            default: 900
            type: integer
        responses:
            200:
                description: Resource metrics
                schema:
                    type: object
                    properties:
                        cpu:
                            type: array
                            description: CPU metrics
                            items:
                                type: object
                                description: CPU metric
                                properties:
                                    date:
                                        type: integer
                                        description: date (timestamp in seconds)
                                        example: 1625097600
                                    value:
                                        type: integer
                                        description: metric value
                                        example: 24
                        ram:
                            type: array
                            description: RAM metrics
                            items:
                                type: object
                                description: RAM metric
                                properties:
                                    date:
                                        type: integer
                                        description: date (timestamp in seconds)
                                        example: 1625097600
                                    value:
                                        type: integer
                                        description: metric value
                                        example: 1200
                        disk_read_io:
                            type: array
                            description: Disk read IO metrics
                            items:
                                type: object
                                description: Disk read IO metric
                                properties:
                                    date:
                                        type: integer
                                        description: date (timestamp in seconds)
                                        example: 1625097600
                                    value:
                                        type: integer
                                        description: metric value
                                        example: 100
                        disk_write_io:
                            type: array
                            description: Disk write IO metrics
                            items:
                                type: object
                                description: Disk write IO metric
                                properties:
                                    date:
                                        type: integer
                                        description: date (timestamp in seconds)
                                        example: 1625097600
                                    value:
                                        type: integer
                                        description: metric value
                                        example: 20
                        network_in_io:
                            type: array
                            description: Network input metrics
                            items:
                                type: object
                                description: Network input metric
                                properties:
                                    date:
                                        type: integer
                                        description: date (timestamp in seconds)
                                        example: 1625097600
                                    value:
                                        type: integer
                                        description: metric value
                                        example: 20
                        network_out_io:
                            type: array
                            description: Network output metrics
                            items:
                                type: object
                                description: Network output metric
                                properties:
                                    date:
                                        type: integer
                                        description: date (timestamp in seconds)
                                        example: 1625097600
                                    value:
                                        type: integer
                                        description: metric value
                                        example: 20
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0224: Wrong integer value
                    - OE0446: "end_date" should be greater than "start_date"
                    - OE0474: interval should be multiple of 900
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            404:
                description: |
                    Not found:
                    - OE0002: Resource not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'cloud_resource', resource_id)
        args = self.get_metric_arguments()
        resource = await run_task(self.controller.get, resource_id)
        res = await self.get_metrics(resource['cloud_account_id'],
                                     resource_id, **args)
        self.write(json.dumps(res))

    async def patch(self, resource_id, **kwargs):
        self.raise405()

    async def delete(self, resource_id, **kwargs):
        self.raise405()
