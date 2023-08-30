import json

from tools.optscale_exceptions.http_exc import OptHTTPError

from tools.optscale_exceptions.common_exc import ForbiddenException

from rest_api.rest_api_server.controllers.assignment import AssignmentAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import run_task, ModelEncoder


class PoolEmployeesAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                          BaseAuthHandler,
                                          BaseHandler):
    def _get_controller_class(self):
        return AssignmentAsyncController

    async def get(self, pool_id, **url_params):
        """
        ---
        description: |
            Get all employees with permissions in target pool
            Required permission: TOKEN
        tags: [assignments]
        summary: Get all employees for provided pool
        parameters:
        -   in: path
            name: pool_id
            description: pool id
            required: true
        -   in: query
            name: exclude_myself
            description: param for exclude current employee from output
            required: false
            type: boolean
            default: false
        responses:
            200:
                description: Employees list
                schema:
                    type: object
                    properties:
                        employees:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string, description:
                                        "Unique employee id"}
                                    name: {type: string, description:
                                        "Employee name"}
                                    deleted_at: {type: integer, description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer, description:
                                        "Created timestamp (service field)"}
                                    organization_id: {type: string,
                                        description: "Employee's organization"}
                                    auth_user_id: {type: string, description:
                                        "Auth user id for employee"}
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            404:
                description: |
                    Not found:
                    - OE0002: Pool not found
            403:
                description: |
                    Forbidden:
                    - OE0378: User is not a member of organization
                    - OE0234: Forbidden
        security:
        - token: []
        """
        exclude_myself = self.get_arg('exclude_myself', bool, False)
        user_id = await self.check_self_auth()
        try:
            res = await run_task(
                self.controller.get_employees_by_permission_in_pool,
                user_id, pool_id, exclude_myself=exclude_myself)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        employee_dict = {'employees': [employee.to_dict()
                                       for employee in res]}
        self.write(json.dumps(employee_dict, cls=ModelEncoder))
