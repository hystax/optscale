import logging

from tornado.web import stream_request_body

from rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api_server.controllers.report_import import (
    ReportImportAsyncController)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task

MAX_BODY_SIZE = 512 * 1024 * 1024   # this is what configured on ingress
LOG = logging.getLogger()


@stream_request_body
class ReportImportAsyncHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return ReportImportAsyncController

    def _validate_post_parameters(self):
        pass

    async def prepare(self):
        await super().prepare()
        # this setting is necessary to avoid getting "Content-Length too long"
        # error from tornado, tornado will not load the whole file into memory
        # due to stream_request_body decorator
        self.request.connection.set_max_body_size(MAX_BODY_SIZE)
        await run_task(self.controller.initialize_upload,
                       self.path_kwargs['cloud_account_id'])

    async def data_received(self, chunk):
        await run_task(self.controller.add_chunk, chunk)

    async def post(self, cloud_account_id):
        """
        ---
        description: |
            Upload billing report for manual import
            Required permission: MANAGE_CLOUD_CREDENTIALS
        tags: [report_upload]
        summary: Upload billing report for manual import
        parameters:
        -   in: path
            name: cloud_account_id
            description: Id of the cloud account for which import is made
            required: true
            type: string
        -   in: body
            name: file
            description: >
                Cloud billing report in CSV format or archive in ZIP or GZ
                format with CSV inside or Parquet file. Swagger 2 doesn't
                support binary file upload, so here it's only possible to
                paste content of the report file into the field
            required: true
            type: string
            format: binary
        responses:
            201:
                description: Success
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: "Unique report upload id"
                        deleted_at:
                            type: integer
                            description: "Deleted timestamp (service field)"
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
        - token: []
        """
        await self.check_permissions(
            'MANAGE_CLOUD_CREDENTIALS', 'cloud_account', cloud_account_id)
        res = await run_task(self.controller.complete_upload,
                             cloud_account_id)
        self.set_status(201)
        self.write(res.to_json())
