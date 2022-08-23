import json
from optscale_exceptions.common_exc import WrongArgumentsException
from optscale_exceptions.http_exc import OptHTTPError
from rest_api_server.controllers.discovery_info_bulk import DiscoveryInfosAsyncBulkController
from rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.exceptions import Err
from rest_api_server.utils import (ModelEncoder, run_task, check_list_attribute)


class DiscoveryInfosAsyncBulkHandler(BaseAsyncCollectionHandler,
                                     BaseAuthHandler):
    def _get_controller_class(self):
        return DiscoveryInfosAsyncBulkController

    @staticmethod
    def _validate_discovery_info(data, string_members=False):
        try:
            if not isinstance(data, dict):
                raise WrongArgumentsException(Err.OE0233, [])
            discovery_info = data.get('discovery_info')
            if discovery_info != []:
                check_list_attribute('discovery_info', discovery_info)
            if string_members:
                for di_id in discovery_info:
                    if not isinstance(di_id, str):
                        raise WrongArgumentsException(
                            Err.OE0218, ['discovery_info', di_id])
            else:
                for di_params in discovery_info:
                    if not isinstance(di_params, dict):
                        raise WrongArgumentsException(Err.OE0217,
                                                      ['discovery_info'])
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)

    async def post(self, cloud_account_id, **url_params):
        """
        ---
        description: |
            Bulk create discovery info for cloud account
            Required permission: CLUSTER_SECRET
        tags: [discovery_info]
        summary: Create discovery info for cloud account
        parameters:
        -   name: cloud_account_id
            in: path
            description: Cloud account id
            required: true
            type: string
        -   in: body
            name: discovery_info
            description: Discovery infos to add
            required: true
            schema:
                type: array
                items:
                    type: object
                    properties:
                        resource_type:
                            type: string
                            required: true
                            description: resource type to discover
                            enum: ['instance', 'volume', 'snapshot', 'rds_instance',
                                  'snapshot_chain', 'bucket', 'k8s_pod']
                        enabled:
                            type: boolean
                            required: false
                            description: is discover enabled for this resource type
        responses:
            200:
                description: Success
            400:
                description: |
                    Wrong arguments:
                    - OE0211: Parameter is immutable
                    - OE0212: Unexpected parameters
                    - OE0216: Argument is not provided
                    - OE0216: discovery_info is not provided
                    - OE0217: Invalid argument
                    - OE0218: discovery_info has incorrect format
                    - OE0226: enabled should be True or False
                    - OE0233: Incorrect request body received
                    - OE0384: Invalid resource type
                    - OE0385: discovery_info should be a list
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Organization/CloudAccount not found
            409:
                description: |
                    Conflict:
                    - OE0518: DiscoveryInfo with type already exists for cloud account
        security:
        - secret: []
        """
        self.check_cluster_secret()
        data = self._request_body()
        self._validate_discovery_info(data)
        res = await run_task(self.controller.create,
                             cloud_account_id, **data)
        result = {'discovery_info': [di.to_dict() for di in res]}
        self.set_status(200)
        self.write(json.dumps(result, cls=ModelEncoder))

    async def delete(self, cloud_account_id, **kwargs):
        """
        ---
        description: |
            Bulk delete discovery infos
            Required permission: CLUSTER_SECRET
        tags: [discovery_info]
        summary: Delete discovery info
        parameters:
        -   name: cloud_account_id
            in: path
            description: cloud account id
            required: true
            type: string
        -   name: discovery_info
            in: body
            description: discovery info ids
            required: true
            type: object
            schema:
                type: array
                items: {type: string,
                        description: "discovery_info ids"}
                example: ["7e7dd1d2-3173-4e14-affc-9e5a9098a1b9",
                          "cc9d0355-14e2-4304-9332-497299b6a5cf"]
        responses:
            204:
                description: Success
            400:
                description: |
                    Wrong arguments:
                    - OE0216: discovery_info is not provided
                    - OE0218: discovery_info has incorrect format
                    - OE0233: Incorrect request body received
                    - OE0385: discovery_info should be a list
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: CloudAccount not found
        security:
        - secret: []
        """
        self.check_cluster_secret(raises=True)
        data = self._request_body()
        self._validate_discovery_info(data, string_members=True)
        await run_task(self.controller.delete,
                       cloud_account_id, **data)
        self.set_status(204)
