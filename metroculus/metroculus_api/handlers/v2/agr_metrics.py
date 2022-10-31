import json
import logging

from metroculus_api.controllers.agr_metrics import AgrMetricsAsyncController
from metroculus_api.handlers.v2.base import SecretHandler
from metroculus_api.utils import ModelEncoder

from optscale_exceptions.common_exc import (
    WrongArgumentsException, UnauthorizedException, NotFoundException)
from optscale_exceptions.http_exc import OptHTTPError

LOG = logging.getLogger(__name__)


class AgrMetricsCollectionHandler(SecretHandler):
    def _get_controller_class(self):
        return AgrMetricsAsyncController

    async def get(self):
        """
        ---
        tags: [agr_metrics]
        summary: Aggregated metrics for resources avg, max, percentile for 0.5 and 0.99
        description: |
            List of average metrics
            Required permission: cluster secret
        parameters:
        -   in: query
            name: cloud_account_id
            description: Cloud account id
            required: true
            type: string
        -   in: query
            name: resource_id
            description: resource_id, repeated
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
            name: meter_name
            description: meter_name (cpu, ram, disk_read_io, disk_write_io,
                network_in_io, network_out_io), repeated
            required: false
            type: string
        responses:
            200:
                description: Metrics for dates
                schema:
                    type: object
                    example:
                        4872fd1d-e519-4bf1-a611-404d112982d7:
                            cpu: {'avg': 12.3, 'max': 30.4, 'qtl50': 10.2, 'qtl99': 25.6}
                            ram: {'avg': 3072, 'max': 4089, 'qtl50': 2902, 'qtl99': 3600}
                            disk_read_io: {'avg': 43, 'max': 80, 'qtl50': 40, 'qtl99': 70}
                            disk_write_io: {'avg': 22, 'max': 50, 'qtl50': 20, 'qtl99': 40}
                            network_in_io: {'avg': 13212, 'max': 15000, 'qtl50': 13000, 'qtl99': 14500}
                            network_out_io: {'avg': 43332, 'max': 56000, 'qtl50': 42003, 'qtl99': 54678}
                        1ba7a0a2-4750-4007-9767-d0b0b6e2701b:
                            cpu: {'avg': 22, 'max': 30.4, 'qtl50': 10.2, 'qtl99': 25.6}
                            ram: {'avg': 1023, 'max': 4089, 'qtl50': 2902, 'qtl99': 3600}
                            disk_read_io: {'avg': 11, 'max': 80, 'qtl50': 40, 'qtl99': 70}
                            disk_write_io: {'avg': 10, 'max': 50, 'qtl50': 20, 'qtl99': 40}
                            network_in_io: {'avg': 2323, 'max': 3453, 'qtl50': 2234, 'qtl99': 2500}
                            network_out_io: {'avg': 4355, 'max': 6500, 'qtl50': 4203, 'qtl99': 6389}
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
            'resource_ids': self.get_arg('resource_id', str, repeated=True),
            'start_date': self.get_arg('start_date', int),
            'end_date': self.get_arg('end_date', int),
            'meter_names': self.get_arg('meter_name', str, repeated=True),
        }
        try:
            res = await self.controller.get(**url_params)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.set_status(200)
        self.write(json.dumps(res, cls=ModelEncoder))
