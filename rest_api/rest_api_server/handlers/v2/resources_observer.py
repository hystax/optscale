from rest_api.rest_api_server.controllers.resource_observer import (
    ResourceObserverAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import run_task


class ResourcesObserverAsyncCollectionHandler(
        BaseAsyncCollectionHandler, BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return ResourceObserverAsyncController

    async def post(self, organization_id):
        """
        ---
        description: |
            Observe resources
            Required permission: CLUSTER_SECRET
        tags: [resources_observer]
        summary: Performs resource specific operations over observed resources
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
            required: true
            type: string
        responses:
            204:
                description: Success
            400:
                description: |
                    Wrong arguments:
                    - OE0456: Duplicate path parameters in the request body
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
                    - OE0002: Organization not found
        security:
        - secret: []
        """
        self.check_cluster_secret(raises=True)
        await run_task(self.controller.observe, organization_id)
        self.set_status(204)


class ResourcesViolationsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                                BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return ResourceObserverAsyncController

    async def post(self, organization_id):
        """
        ---
        description: |
            Process resource violations
            Required permission: CLUSTER_SECRET
        tags: [resources_violations]
        summary: Performs resource specific operations over observed resources
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
            required: true
            type: string
        responses:
            204:
                description: Success
            400:
                description: |
                    Wrong arguments:
                    - OE0456: Duplicate path parameters in the request body
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
                    - OE0002: Organization not found
        security:
        - secret: []
        """
        self.check_cluster_secret(raises=True)
        await run_task(
            self.controller.process_violated_resources, organization_id)
        self.set_status(204)
