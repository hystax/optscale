import json

from rest_api.rest_api_server.controllers.calendar_synchronization import (
    CalendarSynchronizationAsyncController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder

from tools.optscale_exceptions.common_exc import NotFoundException
from tools.optscale_exceptions.http_exc import OptHTTPError


class CalendarSynchronizationAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                                    BaseAuthHandler,
                                                    BaseHandler):
    def _get_controller_class(self):
        return CalendarSynchronizationAsyncController

    async def get(self):
        """
        ---
        description: |
            List calendar synchronization objects.
            Required permission: CLUSTER_SECRET
        tags: [calendar_synchronizations]
        summary: List calendar synchronization objects
        responses:
            200:
                description: calendar synchronizations list
                schema:
                    type: object
                    properties:
                        calendar_synchronizations:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: Unique organization synchronization id
                                    organization_id:
                                        type: string
                                        description: Organization id
                                    calendar_id:
                                        type: string
                                        description: Google calendar id
                                    deleted_at:
                                        type: integer
                                        description: Deleted timestamp (service field)
                                    created_at:
                                        type: integer
                                        description: Created timestamp (service field)
                                    last_completed:
                                        type: integer
                                        description: Last completed synchronization timestamp
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
        security:
        - token: []
        """
        self.check_cluster_secret(raises=True)
        res = await run_task(self.controller.list)
        objs = {'calendar_synchronizations': [r.to_dict() for r in res]}
        self.write(json.dumps(objs, cls=ModelEncoder))

    async def post(self):
        """
        ---
        description: |
            Create calendar synchronization object
            Required permission: CLUSTER_SECRET or EDIT_PARTNER
        tags: [calendar_synchronizations]
        summary: Create calendar synchronization object
        parameters:
        -   in: body
            name: body
            required: true
            schema:
                type: object
                properties:
                    organization_id:
                        type: string
                        description: Organization id
                        required: true
                    calendar_id:
                        type: string
                        description: Google calendar id
                        required: True
                        example: c_dfrcdblt1pnrggfpt7qr4h9k7g@group.calendar.google.com
        responses:
            200:
                description: Success (returns created object)
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Unique organization synchronization id
                        organization_id:
                            type: string
                            description: Organization id
                        calendar_id:
                            type: string
                            description: Google calendar id
                        deleted_at:
                            type: integer
                            description: Deleted timestamp (service field)
                        created_at:
                            type: integer
                            description: Created timestamp (service field)
                        last_completed:
                            type: integer
                            description: Last completed synchronization timestamp
            400:
                description: |
                    Wrong arguments:
                    - OE0003: Database error
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
                    - OE0233: Incorrect request body received
                    - OE0456: Duplicate path parameters in the request body
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
            409:
                description: |
                    Not found:
                    - OE0487: Calendar already linked to organization
            424:
                description: |
                    Failed Dependency:
                    - OE0485: Calendar synchronization is unsupported
                    - OE0489: Unable to create calendar event
                    - OE0493: Calendar validation failed
        security:
        - token: []
        - secret: []
        """
        data = self._request_body()
        organization_id = data.get('organization_id')
        if not organization_id:
            raise OptHTTPError(400, Err.OE0216, ['organization_id'])
        if not isinstance(organization_id, str):
            raise OptHTTPError(400, Err.OE0214, ['organization_id'])
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'EDIT_PARTNER', 'organization', organization_id)
        res = await run_task(self.controller.create, **data)
        self.set_status(201)
        self.write(json.dumps(res.to_dict(), cls=ModelEncoder))


class CalendarSynchronizationAsyncItemHandler(BaseAsyncItemHandler,
                                              BaseAuthHandler,
                                              BaseHandler):
    def _get_controller_class(self):
        return CalendarSynchronizationAsyncController

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing calendar synchronization object
            Required permission: CLUSTER_SECRET
        tags: [calendar_synchronizations]
        summary: Edit calendar synchronization
        parameters:
        -   name: id
            in: path
            description: Calendar synchronization id
            required: true
            type: string
        -   in: body
            name: body
            required: true
            schema:
                type: object
                properties:
                    last_completed:
                        type: integer
                        description: Last completed synchronization timestamp
        responses:
            200:
                description: Success (returns modified object)
            400:
                description: |
                    Wrong arguments:
                    - OE0003: Database error
                    - OE0211: Parameter is immutable
                    - OE0212: Unexpected parameters
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
                    - OE0233: Incorrect request body received
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
                    - OE0002: Calendar synchronization not found
        security:
        - token: []
        """
        self.check_cluster_secret()
        await super().patch(id, **kwargs)

    async def delete(self, id, **kwargs):
        """
        ---
        description: |
            Deletes an existing calendar synchronization
            Required permission: CLUSTER_SECRET or DELETE_PARTNER
        tags: [calendar_synchronizations]
        summary: Delete calendar synchronization
        parameters:
        -   name: id
            in: path
            description: Calendar synchronization id
            required: true
            type: string
        responses:
            204:
                description: Success
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Calendar synchronization not found
            424:
                description: |
                    Failed Dependency:
                    - OE0492: Unable to delete calendar event
        security:
        - token: []
        - secret: []
        """
        try:
            item = await self._get_item(id, **kwargs)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'DELETE_PARTNER', 'organization', item.organization_id)
        await super().delete(id, **kwargs)

    def get(self, id, **kwargs):
        self.raise405()


class OrganizationCalendarAsyncItemHandler(
    CalendarSynchronizationAsyncItemHandler
):
    async def get(self, organization_id, **kwargs):
        """
        ---
        description: |
           Get calendar synchronization object for organization
           Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
        tags: [calendar_synchronizations]
        summary: Get organization calendar synchronization
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
               schema:
                   type: object
                   properties:
                       service_account:
                           type: string
                           description: Service account email
                       calendar_synchronization:
                           type: object
                           description: Calendar synchronization object
                           properties:
                               id:
                                   type: string
                                   description: Unique organization synchronization id
                               organization_id:
                                   type: string
                                   description: Organization id
                               calendar_id:
                                   type: string
                                   description: Google calendar id
                               deleted_at:
                                   type: integer
                                   description: Deleted timestamp (service field)
                               created_at:
                                   type: integer
                                   description: Created timestamp (service field)
                               last_completed:
                                   type: integer
                                   description: Last completed synchronization timestamp
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)

        res = await run_task(
            self.controller.get_service_account)
        response = {'service_account': res}
        calendar_sync = await run_task(
            self.controller.get_by_organization_id, organization_id)
        if calendar_sync:
            response['calendar_synchronization'] = calendar_sync.to_dict()
        self.write(json.dumps(response, cls=ModelEncoder))

    def patch(self, id, **kwargs):
        self.raise405()

    def delete(self, id, **kwargs):
        self.raise405()
