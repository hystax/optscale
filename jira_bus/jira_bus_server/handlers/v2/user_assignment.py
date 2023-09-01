import logging

from jira_bus.jira_bus_server.controllers.user_assignment import (
    UserAssignmentAsyncController,
)
from jira_bus.jira_bus_server.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class UserAssignmentHandler(BaseHandler):
    def _get_controller_class(self):
        return UserAssignmentAsyncController

    async def get(self):
        """
        ---
        description: >
            Get user assignment for current Jira user\n\n
            Required permission: ATLASSIAN(require_account)
        tags: [user_assignment]
        summary: Get user assignment
        responses:
            200:
                description: User assignment
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Unique user assignment id
                        jira_account_id:
                            type: string
                            description: Jira account id
                        auth_user_id:
                            type: string
                            description: OptScale auth user id
                        created_at:
                            type: integer
                            description: Created timestamp (service field)
                        deleted_at:
                            type: integer
                            description: Deleted timestamp (service field)
            404:
                description: |
                    Not found:
                    - OJ0008: user not found
        """
        _, account_id, _ = await self.check_atlassian_auth(
            require_account=True, context_qsh=True
        )
        user_assignment = await self.controller.get_assignment(account_id)
        self.write(user_assignment)

    async def post(self):
        """
        ---
        description: >
            Create or update user assignment for current Jira user.
            Newly-created user assignment needs to be assigned to OptScale
            user using a separate PATCH API call.\n\n
            Required permission: ATLASSIAN(require_account)
        tags: [user_assignment]
        summary: Create or update user assignment
        responses:
            200:
                description: Success
                schema:
                    type: object
                    properties:
                        secret:
                            type: string
                            description: >
                                Unique user secret. Used to match Jira user
                                with OptScale auth user
        """
        _, account_id, _ = await self.check_atlassian_auth(
            require_account=True, context_qsh=True
        )
        secret = await self.controller.create_assignment(account_id)
        self.write({"secret": secret})

    async def patch(self):
        """
        ---
        description: >
            Assign OptScale auth user to Jira user\n\n
            Required permission: TOKEN
        tags: [user_assignment]
        summary: Assign OptScale user to Jira user
        parameters:
        -   in: body
            name: body
            description: request parameters
            required: true
            schema:
                type: object
                properties:
                    secret:
                        type: string
                        description: >
                            Unique user secret, obtained on user assignment
                            create/update
        responses:
            204:
                description: Success
            404:
                description: |
                    Not found:
                    - OJ0008: user not found
        """
        auth_user_id = await self.check_optscale_auth()
        secret = self._request_body().get("secret")
        await self.controller.assign_auth_user(auth_user_id, secret)
        self.set_status(204)

    async def delete(self):
        """
        ---
        description: >
            Delete OptScale user assignment for current Jira user.\n\n
            Required permission: ATLASSIAN(require_account)
        tags: [user_assignment]
        summary: Delete user assignment
        responses:
            204:
                description: Success
            404:
                description: |
                    Not found:
                    - OJ0008: user not found
        """
        _, account_id, _ = await self.check_atlassian_auth(
            require_account=True, context_qsh=True
        )
        await self.controller.delete_assignment(account_id)
        self.set_status(204)
