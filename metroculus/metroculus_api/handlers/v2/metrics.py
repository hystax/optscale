import json
import logging
from tornado import gen

from metroculus_api.controllers.metrics import MetricsAsyncController
from metroculus_api.handlers.v2.base import SecretHandler
from metroculus_api.utils import ModelEncoder

from optscale_exceptions.common_exc import (
    WrongArgumentsException, UnauthorizedException, NotFoundException)
from optscale_exceptions.http_exc import OptHTTPError

LOG = logging.getLogger(__name__)


class MetricsCollectionHandler(SecretHandler):
    def _get_controller_class(self):
        return MetricsAsyncController

    @gen.coroutine
    def get(self):
        """
        ---
        tags: [metrics]
        summary: Metrics for resource
        description: |
            List of metrics
            Required permission: cluster secret
        parameters:
        -   in: query
            name: cloud_account_id
            description: Cloud account id
            required: true
            type: string
        -   in: query
            name: resource_id
            description: resource_id
            required: true
            type: string
        -   in: query
            name: start_date
            description: start_date in timestamp
            required: true
            type: integer
        -   in: query
            name: end_date
            description: end_date in timestamp
            required: true
            type: integer
        -   in: query
            name: interval
            description: interval in seconds, should be a multiple of 900
            required: false
            type: integer
        responses:
            200:
                description: Metrics for dates
                schema:
                    type: object
                    example:
                        cpu:
                            - date: 1627626600
                              value: 24
                            - date: 1627627500
                              value: 12
                        ram:
                            - date: 1627626600
                              value: 1024
                            - date: 1627627500
                              value: 2048
                        network_in_io:
                            - date: 1627626600
                              value: 8000
                            - date: 1627627500
                              value: 4000
            400:
                description: |
                    Wrong arguments:
                    - OM0006: Invalid parameter
                    - OM0008: Parameter is not provided
            401:
                description: |
                    Unauthorized:
                    - OM0007: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OM0005: Bad secret
        security:
        - secret: []
        """
        self.check_cluster_secret()
        url_params = {
            'cloud_account_id': self.get_arg('cloud_account_id', str),
            'resource_id': self.get_arg('resource_id', str),
            'start_date': self.get_arg('start_date', int),
            'end_date': self.get_arg('end_date', int),
            'interval': self.get_arg('interval', int, 900),
        }
        try:
            res = yield gen.Task(
                self.controller.get, **url_params)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.set_status(200)
        self.write(json.dumps(res.result(), cls=ModelEncoder))
