import json
from rest_api_server.controllers.pool_expenses_export import PoolExpensesExportAsyncController
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task, ModelEncoder
from optscale_exceptions.common_exc import NotFoundException
from optscale_exceptions.http_exc import OptHTTPError


class PoolExpensesExportAsyncItemHandler(BaseAsyncItemHandler,
                                         BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return PoolExpensesExportAsyncController

    async def post(self, pool_id):
        """
        ---
        description: |
            Creates a expenses export for the specified pool
            Required permission: MANAGE_POOLS
        tags: [expense_exports]
        summary: Create expense export
        parameters:
        -   name: pool_id
            in: path
            description: id of a pool
            required: true
            type: string
        responses:
            201:
                description: Success
                schema:
                    type: object
                    properties:
                        expenses_export_link:
                            type: string
                            description: expenses export link
                            example: >
                                https://172.22.22.22/restapi/v2/
                                pool_expenses_exports/a57a3b79-0b2e-467f-9a38-bc6870932e74
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
                    - OE0002: Pool/Export not found
            409:
                description: |
                    Conflict:
                    - OE0469: Pool expense export for pool already exists
        security:
        - token: []
        """
        await self.check_permissions(
            'MANAGE_POOLS', 'pool', pool_id)
        res = await run_task(self.controller.create, pool_id)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, pool_id, **kwargs):
        """
        ---
        description: |
            Deletes the specified pool expenses export
            Required permission: MANAGE_POOLS
        tags: [expense_exports]
        summary: Delete expense export
        parameters:
        -   name: pool_id
            in: path
            description: id of a pool
            required: true
            type: string
        responses:
            204:
                description: Success
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
                    - OE0002: Pool/Export not found
        security:
        - token: []
        """
        await self.check_permissions(
            'MANAGE_POOLS', 'pool', pool_id)
        try:
            export = await run_task(self.controller.get_export_by_pool, pool_id)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)
        await run_task(self.controller.delete, export.id)
        self.set_status(204)
