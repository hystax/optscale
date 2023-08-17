import json
from rest_api_server.controllers.report_import import ReportImportAsyncController
from rest_api_server.handlers.v1.base_async import (BaseAsyncCollectionHandler,
                                                    BaseAsyncItemHandler)
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task, ModelEncoder


class ReportImportAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                         BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return ReportImportAsyncController

    def post(self, *args, **kwargs):
        self.raise405()

    async def get(self, cloud_account_id):
        """
        ---
        description: |
            Get list of report imports for cloud account
            Required permission: MANAGE_CLOUD_CREDENTIALS or CLUSTER_SECRET
        tags: [report_imports]
        summary: List of report imports
        parameters:
        -   name: cloud_account_id
            in: path
            description: Cloud account id
            required: true
            type: string
        -   name: show_completed
            in: query
            description: Add completed imports into response
            required: false
            type: boolean
        -   name: show_active
            in: query
            description: Only active imports into response
            required: false
            type: boolean
        responses:
            200:
                description: Report imports list
                schema:
                    type: object
                    properties:
                        report_imports:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: Unique report import id
                                    deleted_at:
                                        type: integer
                                        description: >
                                            Deleted timestamp (service field)
                                    updated_at:
                                        type: integer
                                        description: >
                                            Last update timestamp (service field)
                                    created_at:
                                        type: integer
                                        description: >
                                            Created timestamp (service field)
                                    cloud_account_id:
                                        type: string
                                        description: "Cloud account id"
                                    import_file:
                                        type: string
                                        description: "Import file location"
                                    state:
                                        type: string
                                        description: >
                                            Import state: ('scheduled',
                                            'in_progress','completed','failed')
                                    state_reason:
                                        type: string
                                        description: "Description of the state"
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Cloud account not found
        security:
        - secret: []
        - token: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('MANAGE_CLOUD_CREDENTIALS',
                                         'cloud_account', cloud_account_id)
        show_completed = self.get_arg('show_completed', bool, False)
        show_active = self.get_arg('show_active', bool, False)
        res = await run_task(self.controller.list,
                             cloud_account_id=cloud_account_id,
                             show_completed=show_completed,
                             show_active=show_active)
        report_imports_dict = {
            'report_imports': [r.to_dict() for r in res]}
        self.write(json.dumps(report_imports_dict, cls=ModelEncoder))


class ReportImportAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                                   BaseHandler):
    def _get_controller_class(self):
        return ReportImportAsyncController

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get report import info by ID
            Required permission: MANAGE_CLOUD_CREDENTIALS or CLUSTER_SECRET
        tags: [report_imports]
        summary: Get report import
        parameters:
        -   name: id
            in: path
            description: Report import ID
            required: true
            type: string
        responses:
            200:
                description: Report import
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: "Unique report import id"
                        deleted_at:
                            type: integer
                            description: "Deleted timestamp (service field)"
                        updated_at:
                            type: integer
                            description: "Last update timestamp (service field)"
                        created_at:
                            type: integer
                            description: "Created timestamp (service field)"
                        cloud_account_id:
                            type: string
                            description: "Cloud account id"
                        import_file:
                            type: string
                            description: "Import file location"
                        state:
                            type: string
                            description: >
                                Import state: ('scheduled','in_progress',
                                'completed','failed')
                        state_reason:
                            type: string
                            description: "Description of the state"
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
                    - OE0002: Report import not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('MANAGE_CLOUD_CREDENTIALS',
                                         'report_import', id)
        await super().get(id, **kwargs)

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Patch report import object
            Required permission: CLUSTER SECRET
        tags: [report_imports]
        summary: Patch report import
        parameters:
        -   name: id
            in: path
            description: Report import id
            required: true
            type: string
        -   in: body
            name: body
            description: Report changes
            required: false
            schema:
                type: object
                properties:
                    state:
                        type: string
                        description: >
                            New report import state
                            (scheduled|in_progress|completed|failed)
                    state_reason:
                        type: string
                        description: >
                            Reasoning for the current state, e.g. why failed
        responses:
            200:
                description: Success (returns modified object)
            400:
                description: |
                    Wrong arguments:
                    - OE0214: Should be a string
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            404:
                description: |
                    Not found:
                    - OE0002: Report import is not found
        security:
        - secret: []
        """
        self.check_cluster_secret()
        await super().patch(id, **kwargs)

    async def delete(self, id, **kwargs):
        self.raise405()
