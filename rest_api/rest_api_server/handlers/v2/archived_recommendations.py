import json
from collections import OrderedDict
from datetime import datetime, timezone

from rest_api.rest_api_server.controllers.archived_recommendation import (
    BreakdownArchivedRecommendationsAsyncController,
    ArchivedRecommendationsDetailsAsyncController,
    ArchivedRecommendationsCountAsyncController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import (
    SupportedFiltersMixin, check_int_attribute, ModelEncoder, run_task,
    check_string_attribute)

from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException)
from tools.optscale_exceptions.http_exc import OptHTTPError

HOUR_IN_SECONDS = 3600


class BreakdownArchivedRecommendationsAsyncHandler(SupportedFiltersMixin,
                                                   BaseAsyncItemHandler,
                                                   BaseAuthHandler,
                                                   BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_filters = ['type', 'reason']
        self.bool_filters = []
        self.str_filters = []
        self.int_filters = ['limit']

    def _get_controller_class(self):
        return BreakdownArchivedRecommendationsAsyncController

    def get_filter_arguments(self, args):
        request_arguments = self.request.arguments.keys()
        allowed_args = (list(args.keys()) + self.list_filters +
                        self.bool_filters + self.int_filters +
                        self.str_filters)
        unexpected_args = list(filter(lambda x: x not in allowed_args,
                                      request_arguments))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])
        for filter_name in self.list_filters:
            if filter_name in request_arguments:
                args[filter_name] = self.get_arg(filter_name, str,
                                                 repeated=True)
        for filter_name in self.int_filters:
            args[filter_name] = self.get_arg(filter_name, int, default=None)
            if args[filter_name] is not None:
                try:
                    check_int_attribute(filter_name, args[filter_name],
                                        min_length=1)
                except WrongArgumentsException as exc:
                    raise OptHTTPError.from_opt_exception(400, exc)
        return args

    def get_archive_arguments(self):
        max_date_length = int(datetime.max.replace(
            tzinfo=timezone.utc).timestamp() - 1)
        args = OrderedDict({
            'end_date': self.get_arg('end_date', int),
            'start_date': self.get_arg('start_date', int),
        })
        try:
            for param, value in args.items():
                check_int_attribute(param, value, max_length=max_date_length)
            if args['end_date'] - args['start_date'] < 0:
                raise WrongArgumentsException(
                    Err.OE0446, list(args.keys()))
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        args.update(self.get_filter_arguments(args))
        return args

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get archived recommendations breakdown
            Required permission: INFO_ORGANIZATION
        tags: [archived_recommendations]
        summary: Get archived recommendations breakdown
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: start_date
            in: query
            description: Start date (timestamp in seconds)
            required: true
            type: integer
        -   name: end_date
            in: query
            description: End date (timestamp in seconds)
            required: true
            type: integer
        -   name: type
            in: query
            description: Optimizations module name
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: reason
            in: query
            description: Archiving reason
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: limit
            in: query
            description: Limit records count
            required: false
        responses:
            200:
                description: Breakdown data
                schema:
                    type: object
                    properties:
                        breakdown:
                            type: array
                            items:
                                type: object
                                properties:
                                    count:
                                        type: integer
                                        description: Archived recommendations count
                                        example: 1
                                    module:
                                        type: string
                                        description: Optimizations module name
                                        example: abandoned_kinesis_streams
                                    archived_at:
                                        type: integer
                                        description: Archive date (timestamp in seconds)
                                        example: 1649853214
                                    reason:
                                        type: string
                                        description: Archiving reason
                                        example: resource_deleted
                        start_date:
                            type: integer
                            description: Start date (timestamp in seconds)
                            example: 1643673600
                        end_date:
                            type: integer
                            description: End date (timestamp in seconds)
                            example: 1643673600
                        limit:
                            type: integer
                            description: Max objects amount (limit applied)
                            example: 100
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0224: Wrong integer value
                    - OE0446: "end_date" should be greater than "start_date"
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
                    - OE0002: Organization not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        args = self.get_archive_arguments()
        try:
            res = await run_task(self.controller.get, organization_id, **args)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(404, exc)
        self.write(json.dumps(res, cls=ModelEncoder))


class ArchivedRecommendationsDetailsAsyncHandler(SupportedFiltersMixin,
                                                 BaseAsyncItemHandler,
                                                 BaseAuthHandler,
                                                 BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_filters = []
        self.bool_filters = []
        self.str_filters = ['type', 'reason', 'format']
        self.int_filters = ['archived_at', 'start_date', 'end_date',
                            'start_from', 'limit']

    def _get_controller_class(self):
        return ArchivedRecommendationsDetailsAsyncController

    def get_filter_arguments(self):
        args = {}
        request_arguments = self.request.arguments.keys()
        allowed_args = (self.list_filters + self.bool_filters +
                        self.int_filters + self.str_filters)
        unexpected_args = list(filter(lambda x: x not in allowed_args,
                                      request_arguments))
        if unexpected_args:
            message = ', '.join(unexpected_args)
            raise OptHTTPError(400, Err.OE0212, [message])

        for filter_name in self.str_filters:
            args[filter_name] = self.get_arg(filter_name, str, repeated=False)
            try:
                check_string_attribute(filter_name, args[filter_name],
                                       allow_empty=True)
            except WrongArgumentsException as exc:
                raise OptHTTPError.from_opt_exception(400, exc)

        format_ = args['format']
        if format_ is not None and format_ != 'json':
            raise OptHTTPError(400, Err.OE0473, [args['format']])

        int_filters_validation_params = {
            'archived_at': (None, 1),
            'start_date': (None, 0),
            'end_date': (None, 1),
            'start_from': (0, 0),
            'limit': (None, 1)
        }
        for filter_name in self.int_filters:
            default, min_length = int_filters_validation_params.get(
                filter_name)
            args[filter_name] = self.get_arg(filter_name, int, default=default)
            if args[filter_name] is not None:
                try:
                    check_int_attribute(filter_name, args[filter_name],
                                        min_length=min_length)
                except WrongArgumentsException as exc:
                    raise OptHTTPError.from_opt_exception(400, exc)
        return args

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get archived recommendations details
            Required permission: INFO_ORGANIZATION
        tags: [archived_recommendations]
        summary: Get archived recommendations details
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: archived_at
            in: query
            description: Archive date (timestamp in seconds)
            required: false
            type: integer
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
        -   name: type
            in: query
            description: Optimizations module name
            required: false
            type: string
        -   name: reason
            in: query
            description: Archiving reason
            required: false
            type: string
        -   name: start_from
            in: query
            description: Start records from certain element
            required: false
            type: integer
            default: 0
        -   name: limit
            in: query
            description: Limit records count
            required: false
            type: integer
        -   name: format
            in: query
            description: Output format
            required: false
            type: string
            default: json
            enum: [json]
        responses:
            200:
                description: Details data
                schema:
                    type: object
                    properties:
                        items:
                            type: array
                            items:
                                type: object
                                properties:
                                    module:
                                        type: string
                                        description: Optimizations module name
                                        example: inactive_users
                                    archived_at:
                                        type: integer
                                        description: |
                                            Archive date (timestamp in seconds)
                                        example: 1649853214
                                    reason:
                                        type: string
                                        description: Archiving reason
                                        example: cloud_account_deleted
                                    cloud_account_id:
                                        type: string
                                        description: Cloud account id
                                        example: 8c63e980-6572-4b36-be82-a2bc59705888
                                    cloud_account_name:
                                        type: string
                                        description: Cloud account name
                                        example: AWS main
                                    cloud_type:
                                        type: string
                                        description: Cloud account type
                                        example: aws_cnr
                                    last_used:
                                        type: integer
                                        description: User last used
                                        example: 0
                                    user_id:
                                        type: string
                                        description: User id
                                        example: QWERTY
                                    user_name:
                                        type: string
                                        description: User name
                                        example: unknown
                        count:
                            type: integer
                            description: Archived recommendations count
                            example: 40
                        limit:
                            type: integer
                            description: Max objects amount (limit applied)
                            example: 100
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0224: Wrong integer value
                    - OE0416: Argument should not contain only whitespaces
                    - OE0473: Format is not allowed
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
                    - OE0002: Organization not found
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        args = self.get_filter_arguments()
        format_ = args.pop('format', None)
        try:
            res = await run_task(self.controller.get, organization_id, **args)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(404, exc)
        if format_ == 'json':
            self.set_content_type('application/json; charset="utf-8"')
            self.write(json.dumps(res, cls=ModelEncoder, indent=4,
                                  sort_keys=True))
        else:
            self.write(json.dumps(res, cls=ModelEncoder))


class ArchivedRecommendationsCountAsyncHandler(BreakdownArchivedRecommendationsAsyncHandler):
    DEFAULT_PRECISION = HOUR_IN_SECONDS * 24
    SUPPORTED_PRECISIONS = (
        HOUR_IN_SECONDS,
        HOUR_IN_SECONDS * 3,
        HOUR_IN_SECONDS * 6,
        HOUR_IN_SECONDS * 12,
        HOUR_IN_SECONDS * 24
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_filters = ['type', 'reason']
        self.bool_filters = []
        self.str_filters = []
        self.int_filters = ['precision']

    def _get_controller_class(self):
        return ArchivedRecommendationsCountAsyncController

    def get_archive_arguments(self):
        args = super().get_archive_arguments()
        if args.get('precision'):
            if args['precision'] not in self.SUPPORTED_PRECISIONS:
                raise OptHTTPError(
                    400, Err.OE0520, [', '.join(map(
                        lambda x: str(x), self.SUPPORTED_PRECISIONS))])
        else:
            args['precision'] = self.DEFAULT_PRECISION
        return args

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get archived recommendations count breakdown
            Required permission: INFO_ORGANIZATION
        tags: [archived_recommendations]
        summary: Get archived recommendations count breakdown
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: start_date
            in: query
            description: Start date (timestamp in seconds)
            required: true
            type: integer
        -   name: end_date
            in: query
            description: End date (timestamp in seconds)
            required: true
            type: integer
        -   name: type
            in: query
            description: Optimizations module name
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: reason
            in: query
            description: Archiving reason
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: precision
            in: query
            description: Response precision
            required: false
            type: integer
            default: 86400
            enum: [3600, 10800, 21600, 43200, 86400]
        responses:
            200:
                description: Breakdown data
                schema:
                    type: object
                    properties:
                        breakdown:
                            type: object
                            properties:
                                breakdown_timestamp:
                                    type: object
                                    description: Breakdown timestamp based on precision
                                    properties:
                                        module:
                                            type: object
                                            description: Optimizations module name
                                            properties:
                                                reason:
                                                    type: integer
                                                    description: >
                                                        Archived recommendations count per reason
                            example: {
                            1649853214: {
                                'abandoned_kinesis_streams': {
                                    'resource_deleted': 1,
                                    'recommendation_applied': 2
                                },
                                'obsolete_snapshots': {
                                    'cloud_account_deleted': 41
                                }}}
                        start_date:
                            type: integer
                            description: Start date (timestamp in seconds)
                            example: 1643673600
                        end_date:
                            type: integer
                            description: End date (timestamp in seconds)
                            example: 1643673600
                        count:
                            type: integer
                            description: Archived recommendations count
                            example: 44
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0216: Argument is not provided
                    - OE0217: Invalid query parameter
                    - OE0224: Wrong integer value
                    - OE0446: "end_date" should be greater than "start_date"
                    - OE0520: Precision should be one of supported values
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
                    - OE0002: Organization not found
        security:
        - token: []
        """
        await super().get(organization_id, **url_params)
