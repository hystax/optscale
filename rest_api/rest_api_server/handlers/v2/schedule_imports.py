import json
import logging

from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api.rest_api_server.controllers.report_import import (
    ReportImportScheduleAsyncController)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder

LOG = logging.getLogger()


class ScheduleImportsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                            BaseAuthHandler):
    def _get_controller_class(self):
        return ReportImportScheduleAsyncController

    async def post(self, **url_params):
        """
        ---
        description: |
            Schedule data import for cloud account.
            Required permission: CLUSTER_SECRET, or MANAGE_CLOUD_CREDENTIALS
            when cloud_account_id is specified.
        tags: [report_imports]
        summary: Schedule data import
        parameters:
        -   in: body
            name: body
            description: Report changes
            required: true
            schema:
                type: object
                properties:
                    period:
                        type: integer
                        description: >
                            schedule imports only for account with specified
                            import period
                    organization_id:
                        type: string
                        description: >
                            organization id for import
                    cloud_account_type:
                        type: string
                        description: >
                            specify cloud_account_type for import
                    cloud_account_id:
                        type: string
                        description: >
                            specify cloud_account_id for import
                    priority:
                        type: integer
                        description: >
                            specify priority for import task
                    import_from:
                        type: integer
                        description: >
                            Unix timestamp; import data starting from this
                            date. Only valid with cloud_account_id.
                    import_to:
                        type: integer
                        description: >
                            Unix timestamp; import data up to this date.
                            Only valid with cloud_account_id.
                    reimport:
                        type: boolean
                        description: >
                            bypass ETag check and re-download all files in the
                            selected range. Only valid with cloud_account_id.
        responses:
            200:
                description: Success (returns modified object)
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0223: Should be integer
                    - OE0224: Wrong integer value
                    - OE0226: Should be boolean
                    - OE0528: Cannot use organization_id with cloud_account_id
                    - OE0529: Cannot use cloud_account_type without organization_id
                    - OE0530: Priority should be 1...9
                    - OE0531: Period should be used exclusively
                    - OE0532: Period, organization_id or cloud_account_id is required
                    - OE0533: Invalid cloud account type
                    - OE0446: import_to should be greater than import_from
                    - OE0561: Cannot use import_from/import_to/reimport without cloud_account_id
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
        security:
        - secret: []
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        cloud_account_id = data.get('cloud_account_id')
        if cloud_account_id:
            if not self.check_cluster_secret(raises=False):
                await self.check_permissions(
                    'MANAGE_CLOUD_CREDENTIALS', 'cloud_account',
                    cloud_account_id)
        else:
            self.check_cluster_secret()
        self._validate_params(**data)
        res = await run_task(self.controller.schedule, **data)
        self.set_status(201)
        imports_dict = {'report_imports': [r.to_dict() for r in res]}
        self.write(json.dumps(imports_dict, cls=ModelEncoder))
