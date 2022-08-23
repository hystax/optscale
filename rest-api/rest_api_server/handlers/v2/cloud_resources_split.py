import json

from optscale_exceptions.http_exc import OptHTTPError

from optscale_exceptions.common_exc import (ForbiddenException,
                                            WrongArgumentsException)
from rest_api_server.controllers.assignment import AssignmentAsyncController
from rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task, ModelEncoder, check_list_attribute, \
    check_string_attribute


class SplitResourcesAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                           BaseAuthHandler):
    def _get_controller_class(self):
        return AssignmentAsyncController

    def _validate_params(self, ids):
        try:
            check_list_attribute('resource ids', ids)
            for id in ids:
                check_string_attribute('resource id', id)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)

    async def post(self, organization_id):
        """
        ---
        description: |
            Split provided resources by employee permissions
            Required permission: TOKEN
        tags: [assignments]
        summary: Split resources by permissions
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: body
            description: array of resource ids
            required: true
            schema:
                type: array
                items: {type: string,
                        description: "Resource ids"}
                example: ["7e7dd1d2-3173-4e14-affc-9e5a9098a1b9",
                          "cc9d0355-14e2-4304-9332-497299b6a5cf"]
        responses:
            200:
                description: split lists
                schema:
                    type: object
                    example:
                        owned:
                        - resource_id: d7a8a215-2a61-404c-b4e3-5f1267ea3d0d
                          cloud_account_id: 0f469512-8d88-4509-b5b9-76b14606d616
                          created_at: '2020-04-14T09:02:40'
                          name: OptScale server
                          resource_type: vm
                          employee_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                          cloud_resource_id: f418a69a-4b38-4654-8765-cbbe01bb1202
                          pool_id: 68fe2f98-698d-4726-a7db-5871d8eea137
                          owner_name: Vlad
                          pool_name: Backend
                          pool_purpose: pool
                          cloud_account_name: AWS
                          cloud_type: aws_cnr
                          has_active_transfer: true
                        managed:
                        - resource_id: 9f0c4bab-b142-4b07-b614-a8c88910d9c6
                          cloud_account_id: 0f469512-8d88-4509-b5b9-76b14606d616
                          created_at: '2020-04-16T15:34:44'
                          name: Elastic-1
                          resource_type: vm
                          employee_id: 2c3af462-ac70-46e9-a250-b869644b967c
                          cloud_resource_id: e2fbdb0a-ec34-4db2-aa9f-c924af0835ee
                          pool_id: bf74c051-6a20-4962-86cd-6c4576cb3e16
                          owner_name: Max
                          pool_name: Development
                          pool_purpose: team
                          cloud_account_name: AWS
                          cloud_type: aws_cnr
                          has_active_transfer: true
                        restricted:
                        - resource_id: 36c953d8-f60e-4578-b17e-98659154aa22
                          cloud_account_id: 0f469512-8d88-4509-b5b9-76b14606d617
                          created_at: '2020-05-04T17:01:53'
                          name: Restricted
                          resource_type: vm
                          employee_id: 2c3af462-ac70-46e9-a250-b869644b967c
                          cloud_resource_id: 2bdafad4-dece-4941-b4db-3e399ab815cb
                          pool_id: 0570067b-5272-4a5c-b35d-fd73f625b8d3
                          owner_name: Nick
                          pool_name: futureOps.com
                          pool_purpose: business_unit
                          cloud_account_name: AWS2
                          cloud_type: aws_cnr
                          has_active_transfer: false
            400:
                description: |
                    Wrong arguments:
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0385: Argument should be a list
                    - OE0456: Duplicate path parameters in the request body
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0378: User is not a member of organization
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
        security:
        - token: []
        """
        data = self._request_body()
        self._validate_params(data)
        user_id = await self.check_self_auth()
        try:
            res = await run_task(self.controller.split_resources, user_id,
                                 organization_id, self.token, data)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        self.write(json.dumps(res, cls=ModelEncoder))
