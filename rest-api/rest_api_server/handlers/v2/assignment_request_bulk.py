from optscale_exceptions.http_exc import OptHTTPError

from optscale_exceptions.common_exc import ForbiddenException
from rest_api_server.controllers.assignment_request_bulk import (
    AssignmentRequestAsyncBulkController)
from rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task


class AssignmentRequestAsyncCollectionBulkHandler(BaseAsyncCollectionHandler,
                                                  BaseAuthHandler):
    def _get_controller_class(self):
        return AssignmentRequestAsyncBulkController

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Bulk assignment requests creation
            Required permission: TOKEN
        tags: [assignments]
        summary: Create resource assignment requests in one bulk operation
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: body
            description: resource assignment requests info for bulk
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
                    approver_id:
                        type: string
                        description: "Employee id who should approve/decline
                          these requests"
                        required: True
                        example: bd782b9c-3616-4496-99ae-220743eacd55
                    message:
                        type: string
                        description: "Info message for approver"
                        required: False
                        example: Release this VM for QA team to use
        responses:
            200:
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
                    - OE0212: Unexpected parameters
                    - OE0216: Argument not provided
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0233: Incorrect body received
                    - OE0385: Argument should be a list
                    - OE0454: Invalid pool / owner
                    - OE0456: Duplicate path parameters in the request body
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0381: Not enough permissions for target resource
                    - OE0378: User is not a member of organization
                    - OE0424: Cant create assignment request for the same user
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
            res = await run_task(
                self.controller.create_assignment_requests_bulk,
                user_id, organization_id, self.token, **data)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        self.set_status(200)
        self.write(res)
