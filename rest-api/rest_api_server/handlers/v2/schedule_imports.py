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
        responses:
            200:
                description: Success (returns modified object)
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0223: Should be integer
                    - OE0224: Wrong integer value
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
