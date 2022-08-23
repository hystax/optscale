from optscale_exceptions.http_exc import OptHTTPError

from optscale_exceptions.common_exc import ForbiddenException

from rest_api_server.controllers.assignment_bulk import (
    AssignmentAsyncBulkController)
from rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task


class AssignmentAsyncCollectionBulkHandler(BaseAsyncCollectionHandler,
                                           BaseAuthHandler):
    def _get_controller_class(self):
        return AssignmentAsyncBulkController

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Bulk assign resources to owner and pool
            Required permission: TOKEN
        tags: [assignments]
        summary: Create resource assignments in one bulk operation
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: body
            description: resource assignments info for bulk
            required: true
            schema:
                type: object
                properties:
                    resource_ids:
                        type: array
                        description: "Resource ids"
                        required: True
                        items: {type: string,
                                description: "Resource ids"}
                        example: ["7e7dd1d2-3173-4e14-affc-9e5a9098a1b9",
                                  "cc9d0355-14e2-4304-9332-497299b6a5cf"]
                    owner_id:
                        type: string
                        description: "Employee id for resource ownership"
                        required: False
                        example: bd782b9c-3616-4496-99ae-220743eacd55
                    pool_id:
                        type: string
                        description: "Pool id"
                        required: True
                        example: 68e5c9d5-310b-460f-922c-a1d27d6085d7
                    created_at:
                        type: integer
                        required: False
                        description: >
                            Timestamp for created assignment. Default is curr ts.
                        example: 1591778885
        responses:
            201:
                description: Results for operations inside bulk.
                schema:
                    type: object
                    example:
                        failed:
                        - code: OE0381
                          id: 36c953d8-f60e-4578-b17e-98659154aa22
                          message: Current user doesn't have enough permissions for target resource
                        succeeded:
                        - 6e278b91-25f7-4baf-89ba-b43e92539781
                        - 9f0c4bab-b142-4b07-b614-a8c88910d9c6
                        - d7a8a215-2a61-404c-b4e3-5f1267ea3d0d
            400:
                description: |
                    Wrong arguments:
                    - OE0005: Argument doesn't exist
                    - OE0212: Unexpected parameters
                    - OE0216: Argument not provided
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0233: Incorrect body received
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
                    - OE0379: Target owner doesn't have enough permissions for target pool
                    - OE0380: Current user doesn't have enough permissions for target pool
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
        security:
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        user_id = await self.check_self_auth()
        try:
            res = await run_task(self.controller.create_assignments_bulk,
                                 user_id, organization_id, self.token, **data)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        self.set_status(201)
        self.write(res)
