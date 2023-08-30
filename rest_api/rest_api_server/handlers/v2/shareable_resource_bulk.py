from rest_api.rest_api_server.controllers.shareable_resource_bulk import ShareableResourceBulkAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.exceptions import Err


class ShareableResourceBulkAsyncHandler(BaseAsyncCollectionHandler,
                                        BaseAuthHandler):
    def _get_controller_class(self):
        return ShareableResourceBulkAsyncController

    def _validate_params(self, data):
        resource_ids = data.pop('resource_ids', None)
        if resource_ids is None:
            raise OptHTTPError(400, Err.OE0216, ['resource_ids'])
        if not isinstance(resource_ids, list):
            raise OptHTTPError(400, Err.OE0385, ['resource_ids'])
        if data:
            raise OptHTTPError(400, Err.OE0212, [x for x in data.keys()])

    async def post(self, organization_id):
        """
        ---
        description: |
            Bulk sharing resources
            Required permission: MANAGE_RESOURCES
        tags: [shareable_resources]
        summary: Share several resources in one bulk operation
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: resource_ids
            description: ids of resources to share
            required: true
            type: string
            example: ["7e7dd1d2-3173-4e14-affc-9e5a9098a1b9",
                      "cc9d0355-14e2-4304-9332-497299b6a5cf",
                      "d7a8a215-2a61-404c-b4e3-5f1267ea3d0d",
                      "123"]
        responses:
            201:
                description: Results for operations inside bulk
                schema:
                    type: object
                    example:
                        failed:
                        - code: OE0478
                          id: 7e7dd1d2-3173-4e14-affc-9e5a9098a1b9
                          message: Current resource can't be shared, resource type is invalid for sharing i-1234567890
                        - code: OE0412
                          id: 123
                          message: Resources with ids 123 were not found
                        - code: OE0416
                          id: d7a8a215-2a61-404c-b4e3-5f1267ea3d0d
                          message: Resource i-1234567891 is not active
                        succeeded:
                        - cc9d0355-14e2-4304-9332-497299b6a5cf
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0216: resource_ids is not provided
                    - OE0233: Incorrect body received
                    - OE0385: resource_ids should be a list
            404:
                description: |
                    Not found:
                    - OE0005: Organization doesn't exist
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
        security:
        - token: []
        """
        data = self._request_body()
        resource_ids = data.get('resource_ids')
        self._validate_params(data)
        await self.check_permissions(
            'MANAGE_RESOURCES', 'organization', organization_id)
        res = await run_task(self.controller.bulk_share,
                             organization_id, resource_ids)
        self.set_status(201)
        self.write(res)
