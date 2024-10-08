from rest_api.rest_api_server.controllers.shareable_resource_split import SplitShareableResourceAsyncController
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task
from rest_api.rest_api_server.exceptions import Err
from tools.optscale_exceptions.http_exc import OptHTTPError


class SplitShareableResourceAsyncHandler(BaseAsyncItemHandler,
                                         BaseAuthHandler, BaseHandler):

    def _get_controller_class(self):
        return SplitShareableResourceAsyncController

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Classifies resources by their availability for shareable
            Required permission: MANAGE_RESOURCES
        tags: [shareable_resources]
        summary: Classifies resources by their availability for shareable
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: body
            description: Resource ids
            required: true
            schema:
                type: object
                properties:
                    resource_ids:
                        description: ids of resources
                        required: true
                        type: array
                        items:
                            type: string
                            description: Resource ids
        responses:
            200:
                description: |
                    Lists of eligible, not eligible
                    and already shareable resources
                schema:
                    type: object
                    properties:
                        eligible:
                            type: array
                            items:
                                type: object
                                description: eligible resources for shareable
                        not_eligible:
                            type: array
                            items:
                                type: object
                                description: not eligible resources for shareable
                        already_shareable:
                            type: array
                            items:
                                type: object
                                description: already shareabled resources
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0216: Argument is not provided
                    - OE0385: Resources should be a list
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Resource not found
        security:
        - token: []
        """
        data = self._request_body()
        resources = data.pop('resource_ids', None)
        if resources is None:
            raise OptHTTPError(400, Err.OE0216, ['resource_ids'])
        elif not isinstance(resources, list):
            raise OptHTTPError(400, Err.OE0385, ['resource_ids'])
        if data:
            err_args = ','.join(data.keys())
            raise OptHTTPError(400, Err.OE0212, [err_args])
        await self.check_permissions(
            'MANAGE_RESOURCES', 'organization', organization_id)
        res = await run_task(
            self.controller.split_resources, organization_id, resources)
        self.set_status(200)
        self.write(res)
