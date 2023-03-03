import json
import logging

from rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api_server.controllers.report_import import (
    ReportImportScheduleAsyncController)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task, ModelEncoder

LOG = logging.getLogger()


class ScheduleImportsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                            BaseAuthHandler):
    def _get_controller_class(self):
        return ReportImportScheduleAsyncController

    async def post(self, **url_params):
        """
        ---
        description: |
            Schedule data import for cloud account
            Required permission: CLUSTER SECRET
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
                            organization id
                    cloud_account_type:
                        type: string
                        description: >
                            specify cloud_account_type for import
                            cloud_account_type
                    cloud_account_id:
                        type: string
                        description: >
                            specify cloud_account_id for import
                            cloud_account_id
                    priority:
                        type: integer
                        description: >
                            specify priority for import task
                            priority
        responses:
            200:
                description: Success (returns modified object)
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0223: Should be integer
                    - OE0224: Wrong integer value
                    - OE0528: Cannot use organization_id with cloud_account_id
                    - OE0529: Cannot use cloud_account_type without organization_id
                    - OE0530: Priority should be 1...9
                    - OE0531: Period should be used exclusively
                    - OE0532: Period, organization_id or cloud_account_id is required
                    - OE0533: Invalid cloud account type
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
        """
        self.check_cluster_secret()
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        res = await run_task(self.controller.schedule, **data)
        self.set_status(201)
        imports_dict = {'report_imports': [r.to_dict() for r in res]}
        self.write(json.dumps(imports_dict, cls=ModelEncoder))
