import json
from datetime import datetime

from rest_api.rest_api_server.controllers.cloud_resource import CloudResourceAsyncController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import (run_task, ModelEncoder,
                                            check_int_attribute, object_to_xlsx)
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import (NotFoundException,
                                                  WrongArgumentsException)


class EnvironmentResourcePropertiesHistoryAsyncItemHandler(BaseAsyncItemHandler,
                                                           BaseAuthHandler,
                                                           BaseHandler):
    def _get_controller_class(self):
        return CloudResourceAsyncController

    @staticmethod
    def check_date_arguments(args):
        max_date_length = int(datetime.max.timestamp() - 1)
        date_arg_names = ['end_date', 'start_date']
        for arg_name in date_arg_names:
            if args.get(arg_name) is not None:
                check_int_attribute(arg_name, args.get(arg_name),
                                    max_length=max_date_length)
        if args.get(date_arg_names[0], max_date_length) - args.get(
                date_arg_names[1], 0) < 0:
            raise WrongArgumentsException(Err.OE0446, date_arg_names)

    async def get(self, id):
        """
        ---
        description: |
            Get the history of changes in the properties of
            the environment resource for the specified period
            Required permission: INFO_ORGANIZATION
        tags: [cloud_resources]
        summary: History of changes resource properties
        parameters:
        -   name: id
            in: path
            description: Cloud resource ID
            required: true
            type: string
        -   name: start_date
            in: query
            description: Start date (timestamp in seconds)
            required: false
            type: integer
        -   name: end_date
            in: query
            description: End date (timestamp in seconds)
            required: false
            type: integer
        -   name: format
            in: query
            description: Output format
            required: false
            type: string
            default: advanced_json
            enum: [advanced_json, json, xlsx]
        responses:
            200:
                description: History of changes resource properties
                schema:
                    type: object
                    properties:
                        history:
                            type: array
                            items:
                                type: object
                                properties:
                                    time:
                                        type: integer
                                        description: Timestamp of the change
                                    changes:
                                        type: array
                                        description: List of changes
                                        items:
                                            type: object
                                            properties:
                                                any_property:
                                                    type: object
                                                    description: Contains the old and new property values
                                                    properties:
                                                        old:
                                                            type: string
                                                            description: old value
                                                        new:
                                                            type: string
                                                            description: new value
                            example:
                                - time: 16000000000
                                  changes: [{"version": {"old": 0.1, "new": 0.2}}]
                                - time: 16000000300
                                  changes: [{"version": {"old": 0.2, "new": 0.2}},
                                            {"software": {"old": None, "new": "some_software"}}]
            400:
                description: |
                    Wrong arguments:
                    - OE0480: Resource is not shareable
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
                    - OE0002: Resource not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'cloud_resource', id)
        try:
            args = {}
            start_date = self.get_arg('start_date', int)
            end_date = self.get_arg('end_date', int)
            if start_date is not None:
                args['start_date'] = start_date
            if end_date is not None:
                args['end_date'] = end_date
            self.check_date_arguments(args)
            res = await run_task(self.controller.get_history, id, **args)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        exp_format = self.get_arg('format', str, default='advanced_json')
        if exp_format == 'json':
            response_name, response_dict = res
            self.set_content_type('application/json; charset="utf-8"')
            self.set_header('Content-Disposition',
                            'attachment; filename="%s.%s"' % (
                                response_name, exp_format))
            self.write(json.dumps(
                {'history': response_dict}, cls=ModelEncoder, indent=4,
                sort_keys=True))
        elif exp_format == 'xlsx':
            response_name, response_dict = res
            self.set_content_type('application/vnd.openxmlformats-'
                                  'officedocument.spreadsheetml.sheet')
            self.set_header('Content-Disposition',
                            'attachment; filename="%s.%s"' % (
                                response_name, exp_format))
            self.write(object_to_xlsx(response_dict))
        elif exp_format == 'advanced_json':
            response_name, response_dict = res
            self.write(json.dumps({'history': response_dict}, cls=ModelEncoder))
        else:
            raise OptHTTPError(400, Err.OE0473, [exp_format])

    def patch(self, id, **kwargs):
        self.raise405()

    def delete(self, id, **kwargs):
        self.raise405()


class EnvironmentResourcePropertiesScriptAsyncItemHandler(BaseAsyncItemHandler,
                                                          BaseAuthHandler,
                                                          BaseHandler):
    def _get_controller_class(self):
        return CloudResourceAsyncController

    async def get(self, id):
        """
        ---
        description: |
            Get a script to send the properties of this resource
            Required permission: INFO_ORGANIZATION
        tags: [cloud_resources]
        summary: Get a script to send the properties of this resource
        parameters:
        -   name: id
            in: path
            description: Cloud resource ID
            required: true
            type: string
        responses:
            200:
                description: Script
                schema:
                    type: object
                    properties:
                        script:
                            type: string
                            description: |
                                Get a script to send the properties
                                of this resource
            400:
                description: |
                    Wrong arguments:
                    - OE0480: Resource is not shareable
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
                    - OE0002: Resource not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'cloud_resource', id)
        res = await run_task(self.controller.get_script, id)
        response_dict = {'script': res}
        self.write(json.dumps(response_dict, cls=ModelEncoder))


class EnvironmentResourcePropertiesCollectorAsyncItemHandler(BaseHandler):

    def _get_controller_class(self):
        return CloudResourceAsyncController

    async def post(self, id):
        """
        ---
        description: |
            Registers information about the properties
            of an environment resource
            Required permission: none
        tags: [cloud_resources]
        summary: Registers information about the properties of an environment resource
        parameters:
        -   name: id
            in: path
            description: Cloud resource ID
            required: true
            type: string
        -   in: body
            name: body
            description: new values of resource properties
            required: true
            type: object
            example:
                version: 1.23.4
                status: success
                some_property: some_value
        responses:
            204:
                description: No content
            400:
                description: |
                    Wrong arguments:
                    - OE0233: Incorrect body received
                    - OE0344: Properties should be a dictionary
                    - OE0480: Resource is not shareable
            404:
                description: |
                    Not found:
                    - OE0002: Resource not found
        """
        props = self._request_body()
        await run_task(self.controller.edit, id, env_properties=props)
        self.set_status(204)
