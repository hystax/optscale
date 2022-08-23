import json

from rest_api_server.controllers.checklist import ChecklistAsyncController
from rest_api_server.exceptions import Err
from rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import (
    run_task, ModelEncoder, check_int_attribute)

from optscale_exceptions.http_exc import OptHTTPError
from optscale_exceptions.common_exc import WrongArgumentsException


class ChecklistAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                      BaseAuthHandler):
    def _get_controller_class(self):
        return ChecklistAsyncController

    async def get(self):
        """
        ---
        description: |
            Get list of checklists
            Required permission: CLUSTER_SECRET
        tags: [checklists]
        summary: List of organizations checklists
        responses:
            200:
                description: Checklists list
                schema:
                    type: object
                    properties:
                        checklists:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string, description:
                                        "Unique checklist id"}
                                    deleted_at: {type: integer, description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer, description:
                                        "Created timestamp (service field)"}
                                    organization_id: {type: string, description:
                                        "Organization id"}
                                    last_run: {type: integer, description:
                                        "Last run start timestamp"}
                                    next_run: {type: integer, description:
                                        "Next run start timestamp"}
                                    last_completed: {type: integer, description:
                                        "Last completed run timestamp"}
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
        security:
        - secret: []
        """
        self.check_cluster_secret()
        res = await run_task(self.controller.list)
        checklists = {'checklists': [checklist.to_dict() for checklist in res]}
        self.write(json.dumps(checklists, cls=ModelEncoder))


class ChecklistAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return ChecklistAsyncController

    def _validate_params(self, item, **kwargs):
        params = ['next_run']
        if kwargs.pop('by_cluster_secret', False):
            params.extend(['last_run', 'last_completed'])
        unexpected = list(filter(lambda x: x not in params, kwargs.keys()))
        if unexpected:
            message = ', '.join(unexpected)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            for param in params:
                val = kwargs.get(param)
                if val is not None:
                    check_int_attribute(param, val)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        super()._validate_params(item, **kwargs)

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing checklist
            Required permission: CLUSTER_SECRET or MANAGE_CHECKLISTS
        tags: [checklists]
        summary: Edit checklist
        parameters:
        -   name: id
            in: path
            description: Checklist ID
            required: true
            type: string
        -   in: body
            name: body
            description: Checklist to modify
            required: true
            schema:
                type: object
                properties:
                    last_run:
                        type: integer
                        description: Last run start timestamp
                        required: False
                    next_run:
                        type: integer
                        description: Next run start timestamp.
                            MANAGE_CHECKLISTS permission required
                        required: False
                    last_completed:
                        type: integer
                        description: Last completed run timestamp
                        required: False
        responses:
            200:
                description: Checklist object
                schema:
                    type: object
                    properties:
                        id: {type: string, description:
                            "Unique checklist id"}
                        deleted_at: {type: integer, description:
                            "Deleted timestamp (service field)"}
                        created_at: {type: integer, description:
                            "Created timestamp (service field)"}
                        organization_id: {type: string, description:
                            "Organization id"}
                        last_run: {type: integer, description:
                            "Last run start timestamp"}
                        next_run: {type: integer, description:
                            "Next run start timestamp"}
                        last_completed: {type: integer, description:
                            "Last completed run timestamp"}
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0223: last_run|next_run|last_completed should be integer
                    - OE0224: Value should be between 0 and 2147483647
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
                    - OE0002: Checklist not found
        security:
        - token: []
        - secret: []
        """
        data = self._request_body()
        item = await self._get_item(id)

        by_cluster_secret = True
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'MANAGE_CHECKLISTS', 'organization', item.organization_id)
            by_cluster_secret = False

        self._validate_params(
            item, by_cluster_secret=by_cluster_secret, **data)
        res = await run_task(self.controller.edit, id, **data)
        self.write(res.to_json())
