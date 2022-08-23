from rest_api_server.controllers.cleanup_script import (
    CleanupScriptAsyncController)

from rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task


class CleanupScriptAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return CleanupScriptAsyncController

    def prepare(self):
        self.set_content_type('text/plain')

    async def get(self, cloud_account_id, module_name):
        """
        ---
        description: |
            Get cleanup script for recommendation module
            Required permission: INFO_ORGANIZATION
        tags: [cleanup_scripts]
        summary: Get cleanup script for recommendation module
        produces:
        - text/plain
        responses:
            200:
                description: Cleanup bash script
                schema:
                    type: file
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
                    - OE0002: Cloud account or module not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'cloud_account', cloud_account_id)
        res = await run_task(self.controller.get_script,
                             cloud_account_id, module_name)
        self.set_header('Content-Disposition',
                        'attachment; filename="cleanup_{}_{}.sh"'.format(
                            module_name, cloud_account_id
                        ))
        self.write(res)
