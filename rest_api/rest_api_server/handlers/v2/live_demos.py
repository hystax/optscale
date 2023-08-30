import json

from tools.optscale_exceptions.common_exc import InternalServerError
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.controllers.live_demo import LiveDemoAsyncController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute, is_email_format,
    check_bool_attribute)


class LiveDemoAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                     BaseAuthHandler):

    def _get_controller_class(self):
        return LiveDemoAsyncController

    def prepare(self):
        self.set_content_type()

    def _validate_params(self, **kwargs):
        expected_params = ['email', 'subscribe']
        unexpected = list(
            filter(lambda x: x not in expected_params, kwargs.keys()))
        if unexpected:
            message = ', '.join(unexpected)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            email = kwargs.get('email')
            subscribe = kwargs.get('subscribe')
            if email is not None:
                check_string_attribute('email', email)
                if not is_email_format(email):
                    raise WrongArgumentsException(Err.OE0218, ['Email', email])
            if subscribe is not None:
                check_bool_attribute('subscribe', subscribe)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        super()._validate_params(**kwargs)

    async def post(self):
        """
        ---
        description: Create live demo environment
        tags: [live_demos]
        summary: Create live demo environment
        parameters:
        -   in: body
            name: body
            description: live demo parameters
            required: false
            schema:
                type: object
                properties:
                    email:
                        type: string
                        description: Contact email
                        required: false
                        example: example@mail.com
                    subscribe:
                        type: boolean
                        example: true
                        description: subscribe newsletter
                        required: false
                        default: false
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
        data = self._request_body()
        self._validate_params(**data)
        try:
            res = await run_task(self.controller.create, **data)
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
