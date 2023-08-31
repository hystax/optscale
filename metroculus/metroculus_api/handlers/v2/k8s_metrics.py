import json
import logging

from metroculus.metroculus_api.controllers.k8s_metric import K8sMetricsAsyncController
from metroculus.metroculus_api.handlers.v2.base import SecretHandler
from metroculus.metroculus_api.utils import ModelEncoder

from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, UnauthorizedException, NotFoundException)
from tools.optscale_exceptions.http_exc import OptHTTPError

LOG = logging.getLogger(__name__)


class K8sMetricsCollectionHandler(SecretHandler):
    def _get_controller_class(self):
        return K8sMetricsAsyncController

    async def get(self):
        """
        ---
        tags: [k8s_metrics]
        summary: K8s metrics for cloud account
        description: |
            List of k8s metrics
            Required permission: cluster secret
        parameters:
        -   in: query
            name: cloud_account_id
            description: Cloud account id
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
        responses:
            200:
                description: K8s metrics for dates
                schema:
                    type: object
                    properties:
                        start_date:
                            type: integer
                            description: start date (timestamp in seconds)
                            example: 1500648100
                        end_date:
                            type: integer
                            description: end date (timestamp in seconds)
                            example: 1600327941
                        c2ff1d29-d2f4-4b00-9b81-5f6f7c702cd0:
                            type: array
                            items:
                                type: object
                            example:
                                -   resource_id: ea621719-94dd-4a01-af28-9a0060067fc8
                                    average_pod_cpu_used: 0.6445
                                    pod_cpu_provision: 3
                                    pod_cpu_requests: 3
                                    average_pod_memory_used: 60366848
                                    pod_memory_provision: 262144000
                                    pod_memory_requests: 262144000
                                    total_pod_cpu_requests: 4.5
                                    total_pod_memory_requests: 250366848
                                    total_pod_cpu_used: 2.54
                                    total_pod_memory_used: 120366848
                                    namespace_cpu_provision_used: 6
                                    namespace_memory_provision_used: 150366848
                                    namespace_quota_cpu_provision_hard: 12
                                    namespace_quota_memory_provision_hard: 240366848
                                    namespace_quota_cpu_provision_medium: 8
                                    namespace_quota_memory_provision_medium: 180366848
                                    namespace_quota_cpu_provision_low: 6
                                    namespace_quota_memory_provision_low: 160366848
                                    namespace_cpu_requests_used: 6
                                    namespace_memory_requests_used: 150366848
                                    namespace_quota_cpu_requests_hard: 12
                                    namespace_quota_memory_requests_hard: 240366848
                                    namespace_quota_cpu_requests_medium: 8
                                    namespace_quota_memory_requests_medium: 180366848
                                    namespace_quota_cpu_requests_low: 6
                                    namespace_quota_memory_requests_low: 160366848
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
            'start_date': self.get_arg('start_date', int),
            'end_date': self.get_arg('end_date', int),
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
