from tornado.web import stream_request_body
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.controllers.code_report_upload import CodeReportAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.utils import run_task

MAX_BODY_SIZE = 512 * 1024 * 1024   # this is what configured on ingress
MAX_FILE_SIZE = 10 * 1024 * 1024


@stream_request_body
class CodeReportAsyncHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return CodeReportAsyncController

    def _validate_post_parameters(self):
        pass

    def check_file(self):
        file_size = int(self.request.headers.get('Content-Length', 0))
        if not file_size:
            raise OptHTTPError(400, Err.OE0217, ['file'])
        if file_size > MAX_FILE_SIZE:
            raise OptHTTPError(400, Err.OE0512, [])

    async def prepare(self):
        await super().prepare()
        # this setting is necessary to avoid getting "Content-Length too long"
        # error from tornado, tornado will not load the whole file into memory
        # due to stream_request_body decorator
        self.request.connection.set_max_body_size(MAX_BODY_SIZE)
        self.check_file()
        await run_task(self.controller.initialize_upload,
                       self.path_kwargs['organization_id'])

    async def data_received(self, chunk):
        await run_task(self.controller.add_chunk, chunk)

    async def post(self, organization_id):
        """
        ---
        description: |
            Upload report for technical audit
            Required permission: EDIT_PARTNER
        tags: [technical audit]
        summary: Upload report for technical audit
        parameters:
        -   in: path
            name: organization_id
            description: Id of the organization
            required: true
            type: string
        -   in: body
            name: file
            description: >
                Report in ZIP format (maximum size is 10MB)
            required: true
            type: string
            format: binary
        responses:
            204:
                description: No content
            400:
               description: |
                   Wrong arguments:
                       - OE0217: Invalid file
                       - OE0512: File size limit exceeded
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
                    - OE0002: Organization not found
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization', organization_id)
        await run_task(self.controller.complete_upload, organization_id)
        self.set_status(204)
