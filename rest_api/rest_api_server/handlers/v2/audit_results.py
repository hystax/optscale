from rest_api.rest_api_server.controllers.audit_result import AuditResultAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.utils import run_task


class AuditResultAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return AuditResultAsyncController

    async def get(self, organization_id, audit_id, **kwargs):
        """
        ---
        description: |
            Get audit information
            Required permission: EDIT_PARTNER
        tags: [technical audit]
        summary: Download technical audit results
        parameters:
        -   in: path
            name: organization_id
            description: Organization id
            required: true
        -   in: path
            name: audit_id
            description: Audit id
            required: true
        responses:
            400:
               description: |
                   Wrong arguments:
                       - OE0002: Organization or audit not found
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
        res = await run_task(
            self.controller.download_audit_result, organization_id, audit_id)
        self.set_content_type('application/octet-stream')
        self.write(res)
