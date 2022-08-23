import json

from optscale_exceptions.common_exc import InternalServerError
from optscale_exceptions.http_exc import OptHTTPError
from rest_api_server.controllers.live_demo import LiveDemoAsyncController
from rest_api_server.exceptions import Err
from rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import run_task, ModelEncoder


class LiveDemoAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                     BaseAuthHandler):

    def _get_controller_class(self):
        return LiveDemoAsyncController

    def prepare(self):
        self.set_content_type()

    async def post(self):
        """
        ---
        description: Create live demo environment
        tags: [live_demos]
        summary: Create live demo environment
        responses:
            201:
                description: Created (returns demo environment information)
                schema:
                    type: object
                    example:
                        organization_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        login: 48d85b23511e423ebddc7f7da0bdc6b5@sunflower.demo
                        password: 48d85b23511e423ebddc7f7da0bdc6b5
            409:
                description: |
                    Conflict:
                    - OA0042: User with same email already exists
            500:
                description: |
                    Internal Server Error:
                        - OE0449: Live Demo template missing
                        - OE0450: Failed to load Live Demo template
                        - OE0451: Failed to generate Live Demo organization
        """
        try:
            res = await run_task(self.controller.create)
        except InternalServerError as ex:
            raise OptHTTPError.from_opt_exception(500, ex)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def get(self):
        """
        ---
        description: |
            Validate user demo environment status
            Required permission: TOKEN. API will respond is_active: False if TOKEN missing
        tags: [live_demos]
        summary: Validate user demo environment status
        responses:
            200:
                description: Demo organization status
                schema:
                    type: object
                    example:
                        is_alive: True
        security:
        - token: []
        """
        is_alive = False
        try:
            if self.token:
                user_id = await self.check_self_auth()
                is_alive = await run_task(
                    self.controller.find_demo_organization, user_id)
        except OptHTTPError:
            pass
        self.write(json.dumps({'is_alive': is_alive}, cls=ModelEncoder))
