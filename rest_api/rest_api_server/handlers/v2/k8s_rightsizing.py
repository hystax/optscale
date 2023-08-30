import json
from datetime import datetime, timezone
import logging
from datetime import datetime
from rest_api.rest_api_server.controllers.k8s_rightsizing import (
    K8sRightsizingAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import (run_task, check_int_attribute)
from rest_api.rest_api_server.exceptions import Err
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from tools.optscale_exceptions.http_exc import OptHTTPError

LOG = logging.getLogger(__name__)
DEFAULT_INTERVAL = 900


class K8sRightsizingAsyncHandler(BaseAsyncItemHandler, BaseAuthHandler,
                                 BaseHandler):
    def _get_controller_class(self):
        return K8sRightsizingAsyncController

    def get_k8s_metric_arguments(self):
        args = {
            'start_date': self.get_arg('start_date', int)
        }
        for param, value in args.items():
            if value is None:
                raise OptHTTPError(400, Err.OE0216, [param])
        args.update(
            {
                'end_date': self.get_arg(
                    'end_date', int, default=int(datetime.utcnow().timestamp())
                ),
                'cloud_account_id': self.get_arg('cloud_account_id', str, None)
            })

        unexpected_args = list(filter(lambda x: x not in list(args.keys()),
                                      self.request.arguments.keys()))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])

        self.check_date_arguments(args)
        return args

    @staticmethod
    def check_date_arguments(args):
        max_date_length = int(datetime.max.replace(
            tzinfo=timezone.utc).timestamp() - 1)
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

    async def get(self, organization_id):
        """
        ---
        description: |
            Get k8s rightsizing
            Required permission: INFO_ORGANIZATION
        tags: [k8s_rightsizing]
        summary: Get k8s rightsizing
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
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
        -   name: cloud_account_id
            in: query
            description: Cloud account ID
            required: false
            type: string
        responses:
            200:
                description: K8s Rightsizing
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
                        k8s_app_rightsizing:
                            type: array
                            items:
                                type: object
                                properties:
                                    cloud_account_id:
                                        type: string
                                        description: K8s Cloud Account ID
                                        example: ef54ceb3-03dc-4849-a1e9-f14a544793c7
                                    cloud_account_name:
                                        type: string
                                        description: K8s Cloud Account Name
                                        example: K8s Dev
                                    name:
                                        type: string
                                        description: K8s application name
                                        example: prometheus
                                    namespace:
                                        type: string
                                        description: K8s application namespace
                                        example: optscale
                                    cluster:
                                        type: string
                                        description: K8s application cluster
                                        example: test_cluster
                                    average_pod_cpu_used:
                                        type: number
                                        description: Sum of average cpu by pods from k8s application
                                        example: 0.3176
                                    pod_cpu_provision:
                                        type: number
                                        description: Sum of cpu provision by pods from k8s application
                                        example: 17.20
                                    pod_cpu_requests:
                                        type: number
                                        description: Sum of cpu requests by pods from k8s application
                                        example: 8
                                    total_pod_cpu_requests:
                                        type: number
                                        description: >
                                            Total number of requests cpu spreaded by hours by pods from k8s
                                            application within interval
                                        example: 24
                                    average_pod_memory_used:
                                        type: number
                                        description: Sum of average memory by pods from k8s application
                                        example: 9285632.0
                                    pod_memory_provision:
                                        type: number
                                        description: Sum of memory provision by pods from k8s application
                                        example: 5767168000.0
                                    pod_memory_requests:
                                        type: number
                                        description: Sum of memory requests by pods from k8s application
                                        example: 5767168000.0
                                    total_pod_memory_requests_gb:
                                        type: number
                                        description: >
                                            Total number of requests memory spreaded by hours by pods from
                                            k8s application within interval
                                        example: 1.734
                                    total_pod_cpu_hours:
                                        type: number
                                        description: Sum of cpu in hours by pods from k8s application
                                        example: 0.0148
                                    total_pod_memory_gb:
                                        type: number
                                        description: Sum of memory in gb by pods from k8s application
                                        example: 1.452
                                    namespace_cpu_provision_used:
                                        type: number
                                        description: Sum of cpu namespace resources provision used
                                        example: 0.8
                                    namespace_memory_provision_used:
                                        type: number
                                        description: Sum of memory namespace resources provision used
                                        example: 838860800.0
                                    namespace_quota_cpu_provision_hard:
                                        type: number
                                        description: Namespace resource quota cpu for hard priority pods
                                        example: 2
                                    namespace_quota_memory_provision_hard:
                                        type: number
                                        description: Namespace resource quota memory for hard priority pods
                                        example: 2147483648
                                    namespace_quota_cpu_provision_medium:
                                        type: number
                                        description: Namespace resource quota cpu for medium priority pods
                                        example: 1
                                    namespace_quota_memory_provision_medium:
                                        type: number
                                        description: Namespace resource quota memory for medium priority pods
                                        example: 1147483648
                                    namespace_quota_cpu_provision_low:
                                        type: number
                                        description: Namespace resource quota cpu for low priority pods
                                        example: 0.8
                                    namespace_quota_memory_provision_low:
                                        type: number
                                        description: Namespace resource quota memory for low priority pods
                                        example: 847483648
                                    namespace_cpu_requests_used:
                                        type: number
                                        description: Sum of cpu namespace resources requests used
                                        example: 0.8
                                    namespace_memory_requests_used:
                                        type: number
                                        description: Sum of memory namespace resources requests used
                                        example: 838860800.0
                                    namespace_quota_cpu_requests_hard:
                                        type: number
                                        description: Namespace requests quota cpu for hard priority pods
                                        example: 2
                                    namespace_quota_memory_requests_hard:
                                        type: number
                                        description: Namespace requests quota memory for hard priority pods
                                        example: 2147483648
                                    namespace_quota_cpu_requests_medium:
                                        type: number
                                        description: Namespace requests quota cpu for medium priority pods
                                        example: 1
                                    namespace_quota_memory_requests_medium:
                                        type: number
                                        description: Namespace requests quota memory for medium priority pods
                                        example: 1147483648
                                    namespace_quota_cpu_requests_low:
                                        type: number
                                        description: Namespace requests quota cpu for low priority pods
                                        example: 0.8
                                    namespace_quota_memory_requests_low:
                                        type: number
                                        description: Namespace requests quota memory for low priority pods
                                        example: 847483648
            400:
                description: |
                    Wrong arguments:
                    - OE0005: Argument doesn't exist
                    - OE0212: Unexpected parameters
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0224: Wrong integer value
                    - OE0446: "end_date" should be greater than "start_date"
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        args = self.get_k8s_metric_arguments()
        k8s_rightsizing = await run_task(self.controller.get,
                                         organization_id=organization_id,
                                         **args)
        self.write(json.dumps(k8s_rightsizing))

    async def patch(self, resource_id, **kwargs):
        self.raise405()

    async def delete(self, resource_id, **kwargs):
        self.raise405()
