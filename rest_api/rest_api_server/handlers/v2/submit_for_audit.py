from rest_api.rest_api_server.controllers.submit_for_audit import AuditSubmitAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task


class AuditSubmitAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return AuditSubmitAsyncController

    async def post(self, organization_id):
        """
        ---
        description: |
            Submit organization for technical audit
            Required permission: EDIT_PARTNER
        tags: [technical audit]
        summary: Submit organization for technical audit
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            204:
                description: No content
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
        await run_task(self.controller.submit, organization_id)
        self.set_status(204)
