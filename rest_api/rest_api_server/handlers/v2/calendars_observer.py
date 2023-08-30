from rest_api.rest_api_server.controllers.calendar_observer import (
    CalendarObserverAsyncController)
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import run_task


class CalendarsObserverAsyncCollectionHandler(
        BaseAsyncCollectionHandler, BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return CalendarObserverAsyncController

    async def post(self, organization_id):
        """
        ---
        description: |
            Observe organizations linked calendars
            Required permission: CLUSTER_SECRET
        tags: [calendars_observer]
        summary: Observe organizations linked calendars
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
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
                    - OE0486: Calendar synchronization not found for organization
            424:
                description: |
                    Failed Dependency:
                    - OE0490: Unable to list calendar event
                    - OE0491: Calendar tp modify calendar event
        security:
        - secret: []
        """
        self.check_cluster_secret(raises=True)
        await run_task(self.controller.observe, organization_id)
        self.set_status(204)
