import json
from datetime import datetime, timezone
from bson import ObjectId

from tools.optscale_exceptions.common_exc import (NotFoundException,
                                                  WrongArgumentsException)
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.controllers.pool import PoolAsyncController
from rest_api.rest_api_server.controllers.expense import (
    RawExpenseAsyncController, CleanExpenseAsyncController,
    RegionExpenseAsyncController, SummaryExpenseAsyncController)
from rest_api.rest_api_server.controllers.employee import EmployeeAsyncController
from rest_api.rest_api_server.controllers.cloud_account import CloudAccountAsyncController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler

from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_int_attribute, object_to_xlsx,
    SupportedFiltersMixin, check_regex_attribute)


class ExpenseBaseAsyncHandler(BaseAsyncItemHandler, BaseAuthHandler, BaseHandler):
    FILTERS = []

    @staticmethod
    def check_date_arguments(args):
        max_date_length = int(datetime.max.replace(
            tzinfo=timezone.utc).timestamp() - 1)
        date_arg_names = ['end_date', 'start_date']

        try:
            for arg_name in date_arg_names:
                check_int_attribute(
                    arg_name, args[arg_name], max_length=max_date_length)
            if args[date_arg_names[0]] - args[date_arg_names[1]] < 0:
                raise WrongArgumentsException(
                    Err.OE0446, date_arg_names)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)

    def get_expense_arguments(self, filter_required=True):
        args = {
            'start_date': self.get_arg('start_date', int),
            'end_date': self.get_arg('end_date', int),
            'filter_by': self.get_arg('filter_by', str),
        }
        for param, value in args.items():
            if param == 'filter_by' and not filter_required:
                continue
            if value is None:
                raise OptHTTPError(400, Err.OE0216, [param])

        self.check_date_arguments(args)

        filter_by = args['filter_by']
        if filter_by and filter_by not in self.FILTERS:
            raise OptHTTPError(400, Err.OE0217, ['filter_by'])
        return args


class ExpenseAsyncPoolHandler(ExpenseBaseAsyncHandler):
    FILTERS = ['cloud', 'pool', 'employee']

    def _get_controller_class(self):
        return PoolAsyncController

    async def get(self, pool_id):
        """
        ---
        description: |
            Get expenses by pool ID
            Required permission: INFO_ORGANIZATION
        tags: [expenses]
        summary: Get pool expenses
        parameters:
        -   name: pool_id
            in: path
            description: Pool ID
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
        -   name: filter_by
            in: query
            description: Filtered By (”cloud” | “pool” | “employee”)
            required: false
            type: string
        responses:
            200:
                description: Expenses data
                schema:
                    type: object
                    properties:
                        expenses:
                            type: object
                            properties:
                                total: {type: integer,
                                    description: "Total value of expenses"}
                                previous_total:
                                    type: integer
                                    description: >
                                        The amount of expenses for the previous period in days, identical to the period
                                        in the request (f.e. if start_date is the beginning of a calendar week and
                                        end_date is the end of the same week, then previous_total will contain the
                                        amount of expenses for the previous week relative to the requested one)
                                previous_range_start:
                                    type: integer
                                    description: >
                                        UTC timestamp of the start of previous
                                        range used for previous_total calculation
                                id: {type: string,
                                    description: "Unique object id"}
                                name: {type: string,
                                    description: "Object Name"}
                                Pool_id: {type: string,
                                    description: "Pool id"}
                                type: {type: string,
                                    description: "Object type"}
                                breakdown:
                                    type: object
                                    properties:
                                        1585310604:
                                            type: array
                                            items:
                                                type: object
                                                properties:
                                                    id: {type: string,
                                                        description: "Unique object id"}
                                                    name: {type: string,
                                                        description: "Object Name"}
                                                    type: {type: string,
                                                        description: "Object type"}
                                                    expense: {type: integer,
                                                        description: "Total value of expenses"}
                                                    purpose: {type: string,
                                                        description: "Pool purpose"}
                                ”cloud | pool | employee”:
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            id: {type: string,
                                                description: "Unique filtered object id"}
                                            name: {type: string,
                                                description: "Organization display name"}
                                            type: {type: string,
                                                description: "Filtered type name"}
                                            total: {type: integer,
                                                description: "Filtered object expense value"}
                                            purpose: {type: string,
                                                description: "Pool purpose"}
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0216: Argument is not provided
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer value
                    - OE0446: "end_date" should be greater than "start_date"
            401: {description: "Unauthorized: \n\n
                - OE0235: Unauthorized\n\n
                - OE0237: This resource requires authorization"}
            403: {description: "Forbidden: \n\n
                - OE0234: Forbidden"}
            404: {description: "Not found: \n\n
                - OE0002: Pool not found"}
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'pool', pool_id)
        try:
            pool = await self._get_item(pool_id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)

        args = self.get_expense_arguments(filter_required=False)

        res = await run_task(self.controller.get_expenses, pool, **args)
        self.write(json.dumps(res, cls=ModelEncoder))


class ExpenseAsyncCloudHandler(ExpenseBaseAsyncHandler):
    FILTERS = ["service", "region", "pool", "employee", "resource_type",
               "k8s_node", "k8s_namespace", "k8s_service"]

    def _get_controller_class(self):
        return CloudAccountAsyncController

    async def get(self, cloud_account_id, **url_params):
        """
        ---
        description: |
            Get expenses by cloud_account_id
            Required permission: INFO_ORGANIZATION
        tags: [expenses]
        summary: Get cloud account expenses
        parameters:
        -   name: cloud_account_id
            in: path
            description: Cloud account id for getting expenses
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
        -   name: filter_by
            in: query
            description: Filtered By (”service” | “region” | “pool” |
                         “employee” | “resource_type” | ”k8s_node” | ”k8s_namespace” | ”k8s_service”)
            required: true
            type: string
        responses:
            200:
                description: Expenses data
                schema:
                    type: object
                    properties:
                        expenses:
                            type: object
                            properties:
                                total: {type: integer,
                                    description: "Total value of expenses"}
                                previous_total:
                                    type: integer
                                    description: >
                                        The amount of expenses for the previous period in days, identical to the period
                                        in the request (f.e. if start_date is the beginning of a calendar week and
                                        end_date is the end of the same week, then previous_total will contain the
                                        amount of expenses for the previous week relative to the requested one)
                                previous_range_start:
                                    type: integer
                                    description: >
                                        UTC timestamp of the start of previous
                                        range used for previous_total calculation
                                id: {type: string,
                                    description: "Unique object id"}
                                name: {type: string,
                                    description: "Object Name"}
                                type: {type: string,
                                    description: "Object type"}
                                breakdown:
                                    type: object
                                    properties:
                                        1585310604:
                                            type: array
                                            items:
                                                type: object
                                                properties:
                                                    id: {type: string,
                                                        description: "Unique object id"}
                                                    name: {type: string,
                                                        description: "Object Name"}
                                                    type: {type: string,
                                                        description: "Object type"}
                                                    expense: {type: integer,
                                                        description: "Total value of expenses"}
                                ”service|region|pool|employee|resource_type”|”k8s_node”|”k8s_namespace”|”k8s_service”:
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            id: {type: string,
                                                description: "Unique filtered object id"}
                                            name: {type: string,
                                                description: "Organization display name"}
                                            type: {type: string,
                                                description: "Filtered type name"}
                                            total: {type: integer,
                                                description: "Filtered object expense value"}
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0216: Argument is not provided
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer value
                    - OE0446: "end_date" should be greater than "start_date"
            401: {description: "Unauthorized: \n\n
                - OE0235: Unauthorized\n\n
                - OE0237: This resource requires authorization"}
            403: {description: "Forbidden: \n\n
                - OE0234: Forbidden"}
            404: {description: "Not found: \n\n
                - OE0002: Cloud account not found"}
        security:
        - token: []
        """
        await self.check_permissions('INFO_ORGANIZATION', 'cloud_account',
                                     cloud_account_id)
        try:
            cloud_acc = await self._get_item(cloud_account_id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)

        args = self.get_expense_arguments()
        res = await run_task(self.controller.get_expenses, cloud_acc, **args)
        self.write(json.dumps(res, cls=ModelEncoder))


class ExpenseAsyncEmployeeHandler(ExpenseBaseAsyncHandler):
    FILTERS = ["pool", "cloud"]

    def _get_controller_class(self):
        return EmployeeAsyncController

    async def get(self, employee_id, **url_params):
        """
        ---
        description: |
            Get expenses by employee ID
            Required permission: INFO_ORGANIZATION
        tags: [expenses]
        summary: Get employee expenses
        parameters:
        -   name: employee_id
            in: path
            description: employee Expenses
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
        -   name: filter_by
            in: query
            description: Filtered By (”pool” | ”cloud”)
            required: true
            type: string
        responses:
            200:
                description: Expenses data
                schema:
                    type: object
                    properties:
                        expenses:
                            type: object
                            properties:
                                total: {type: integer,
                                    description: "Total value of expenses"}
                                previous_total:
                                    type: integer
                                    description: >
                                        The amount of expenses for the previous period in days, identical to the period
                                        in the request (f.e. if start_date is the beginning of a calendar week and
                                        end_date is the end of the same week, then previous_total will contain the
                                        amount of expenses for the previous week relative to the requested one)
                                previous_range_start:
                                    type: integer
                                    description: >
                                        UTC timestamp of the start of previous
                                        range used for previous_total calculation
                                id: {type: string,
                                    description: "Unique object id"}
                                name: {type: string,
                                    description: "Object Name"}
                                type: {type: string,
                                    description: "Object type"}
                                breakdown:
                                    type: object
                                    properties:
                                        1585310604:
                                            type: array
                                            items:
                                                type: object
                                                properties:
                                                    id: {type: string,
                                                        description: "Unique object id"}
                                                    name: {type: string,
                                                        description: "Object Name"}
                                                    type: {type: string,
                                                        description: "Object type"}
                                                    expense: {type: integer,
                                                        description: "Total value of expenses"}
                                ”pool | cloud”:
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            id: {type: string,
                                                description: "Unique filtered object id"}
                                            name: {type: string,
                                                description: "Employee display name"}
                                            type: {type: string,
                                                description: "Filtered type name"}
                                            total: {type: integer,
                                                description: "Filtered object expense value"}
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0216: Argument is not provided
                    - OE0223: Argument should be integer
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
                    - OE0002: Employee not found
        security:
        - token: []
        """
        await self.check_permissions('INFO_ORGANIZATION', 'employee', employee_id)
        try:
            employee = await self._get_item(employee_id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)

        args = self.get_expense_arguments()
        res = await run_task(self.controller.get_expenses, employee, **args)
        self.write(json.dumps(res, cls=ModelEncoder))


class RegionExpenseAsyncCloudHandler(ExpenseBaseAsyncHandler):

    def _get_controller_class(self):
        return RegionExpenseAsyncController

    def get_expense_arguments(self, filter_required=False):
        args = super().get_expense_arguments(filter_required=filter_required)
        args.pop('filter_by', None)
        return args

    async def get(self, organization_id):
        """
        ---
        description: |
            Get region expenses
            Required permission: INFO_ORGANIZATION
        tags: [expenses]
        summary: Get region expenses
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
        responses:
            200:
                description: Expenses data
                schema:
                    type: object
                    properties:
                        expenses:
                            type: object
                            properties:
                                total: {type: integer,
                                    description: "Total value of expenses"}
                                previous_total:
                                    type: integer
                                    description: >
                                        The amount of expenses for the previous period in days, identical to the period
                                        in the request (f.e. if start_date is the beginning of a calendar week and
                                        end_date is the end of the same week, then previous_total will contain the
                                        amount of expenses for the previous week relative to the requested one)
                                previous_range_start:
                                    type: integer
                                    description: >
                                        UTC timestamp of the start of previous
                                        range used for previous_total calculation
                                ”regions”:
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            id: {type: string,
                                                description: "Region id"}
                                            name: {type: string,
                                                description: "Region name"}
                                            total: {type: number,
                                                description: "Region total expense value"}
                                            previous_total:
                                                type: integer
                                                description: >
                                                    The amount of expenses for the previous period in days in region,
                                                    identical to the period in the request (f.e. if start_date is the
                                                    beginning of a calendar week and end_date is the end of the same
                                                    week, then previous_total will contain the amount of expenses for
                                                    the previous week relative to the requested one)
                                            longitude: {type: number,
                                                description: "Region longitude"}
                                            latitude: {type: number,
                                                description: "Region latitude"}
                                            type: {type: string,
                                                description: "Cloud type"}
            424:
                description: |
                    Failed dependency
                    - OE0445: Organization doesn't have any cloud accounts connected
            404:
                description: |
                    Not found
                    - OE0002: Organization not found
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0216: Argument is not provided
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer value
                    - OE0446: "end_date" should be greater than "start_date"
        security:
        - token: []
        """
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', organization_id)
        args = self.get_expense_arguments()
        args.pop('filter_by', None)
        expenses = await run_task(self.controller.get_expenses, organization_id, **args)
        self.write(json.dumps({'expenses': expenses}, cls=ModelEncoder))


class MongoEncoder(ModelEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


class FilteredExpensesBaseAsyncHandler(SupportedFiltersMixin,
                                       ExpenseBaseAsyncHandler):
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
        for filter_name in self.str_filters:
            if filter_name in request_arguments:
                args[filter_name] = self.get_arg(
                    filter_name, str, repeated=False)
                if args[filter_name] is not None:
                    try:
                        check_regex_attribute(filter_name, args[filter_name])
                    except WrongArgumentsException as exc:
                        raise OptHTTPError.from_opt_exception(400, exc)
        for filter_name in self.bool_filters:
            if filter_name in request_arguments:
                args[filter_name] = self.get_arg(filter_name, bool, default=None)
        for filter_name in self.int_filters:
            args[filter_name] = self.get_arg(filter_name, int, default=None)
            if args[filter_name] is not None:
                try:
                    check_int_attribute(filter_name, args[filter_name],
                                        min_length=1)
                except WrongArgumentsException as exc:
                    raise OptHTTPError.from_opt_exception(400, exc)
        return args

    def get_expense_arguments(self, filter_required=True):
        args = super().get_expense_arguments(filter_required=False)
        args.pop('filter_by', None)
        args.update(self.get_filter_arguments(args))
        return args

    async def get(self, organization_id, **url_params):
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        args = self.get_expense_arguments()
        try:
            res = await run_task(self.controller.get, organization_id, **args)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(404, exc)
        self.write(json.dumps(res, cls=ModelEncoder))


class CleanExpenseAsyncHandler(FilteredExpensesBaseAsyncHandler):
    expenses_key = 'clean_expenses'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.str_filters.append('format')
        self.int_filters.append('limit')
        self.list_filters.append('field')

    def _get_controller_class(self):
        return CleanExpenseAsyncController

    def _fix_expenses_data(self, expenses_data):
        """
        OS-4055: workaround to fix issue for xlsx generation, as for
        different clouds we have different schema for security groups
        """
        for ed in expenses_data:
            # converting OrderedDicts SGs into strings
            sgs = ed.get('security_groups', [])
            if len(sgs) and not isinstance(sgs[0], str):
                ed['security_groups'] = [str(sg) for sg in sgs]

            # pop recommendations
            for exclude in [
                'recommendations',
                'excluded_recommendations',
                'dismissed_recommendations'
            ]:
                ed.pop(exclude, None)

        return expenses_data

    def _filter_expense_fields(self, expense: dict, fields_to_keep: list[list[str]]) -> dict:
        """
        Implements response fields whitelisting for a specific element in expenses response.
        """
        if not isinstance(expense, dict):
            return expense
        processed_expense = {}
        for field_list in fields_to_keep:
            if not field_list:
                continue
            first_field = field_list[0]
            value = expense.get(first_field)
            if value is None:
                continue
            if len(field_list) > 1:
                # provided whitelist field is complex, e.g. "owner.id".
                # need to read out the value of the "owner" key and
                # perform whitelisting for the underlying dict.
                value = self._filter_expense_fields(value, [field_list[1:]])
            processed_expense[first_field] = value
        return processed_expense

    def _filter_response_fields(self, response, fields_to_keep):
        """
        Implements response fields whitelisting.
        Given a list of fileds to keep ["id", "owner.id"], turns response:
        [
            {
                "id": "1",
                "owner": {
                    "id": "1",
                    "name": "2"
                },
                "cost": 0
            }
        ]

        into a filtered response:
        [
            {
                "id": "1",
                "owner": {
                    "id": "1"
                }
            }
        ]
        """
        if not fields_to_keep:
            return
        expenses = response.get(self.expenses_key)
        if expenses is None:
            return
        processed_expenses = []
        fields_to_keep = [field.split(".") for field in fields_to_keep]
        for expense in expenses:
            processed_expenses.append(self._filter_expense_fields(expense, fields_to_keep))
        response[self.expenses_key] = processed_expenses

    def _respond_data(self, exp_format, response, fields=None):
        self._filter_response_fields(response, fields)
        if exp_format == 'json':
            self.set_content_type('application/json; charset="utf-8"')
            expenses = response.get(self.expenses_key)
            result = expenses if expenses is not None else response
            self.write(json.dumps(result, cls=ModelEncoder, indent=4,
                                  sort_keys=True))
        elif exp_format == 'xlsx':
            self.set_content_type('application/vnd.openxmlformats-'
                                  'officedocument.spreadsheetml.sheet')
            expenses = response.get(self.expenses_key)
            res_exp = expenses if expenses is not None else [response]
            res_exp = self._fix_expenses_data(res_exp)
            res_str = json.dumps(res_exp, cls=MongoEncoder)
            self.write(object_to_xlsx(json.loads(res_str)))
        elif exp_format == 'advanced_json':
            self.write(json.dumps(response, cls=MongoEncoder))
        else:
            raise OptHTTPError(400, Err.OE0473, [exp_format])

    async def get(self, organization_id, **url_params):
        # language=yaml
        """
        ---
        description: |
            Get clean expenses
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [expenses]
        summary: Get clean expenses
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
        -   name: cloud_account_id
            in: query
            description: cloud account id
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: pool_id
            in: query
            description: >
                handle pool id (and it's children if pool_id ends with a + sign)
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: owner_id
            in: query
            description: resource owner id
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: region
            in: query
            description: region
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: service_name
            in: query
            description: service_name
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: resource_type
            in: query
            description: >
                resource_type in format resource_type:type_resource_type.
                Supported type_resource_type values - [regular, cluster, environment]
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: active
            in: query
            description: Active
            required: false
            type: boolean
        -   name: recommendations
            in: query
            description: Recommendations
            required: false
            type: boolean
        -   name: constraint_violated
            in: query
            description: constraint_violated
            required: false
            type: boolean
        -   name: created_by_kind (for kubernetes only)
            in: query
            description: created_by_kind
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: created_by_name (for kubernetes only)
            in: query
            description: created_by_name
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: k8s_namespace (for kubernetes only)
            in: query
            description: k8s_namespace
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: k8s_node (for kubernetes only)
            in: query
            description: k8s_node
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: k8s_service (for kubernetes only)
            in: query
            description: k8s_service
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: tag
            in: query
            description: tag name
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: without_tag
            in: query
            description: tag name
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: limit
            in: query
            description: >
                Limit amount of expenses returned. Must be >0. Expenses will be
                sorted by cost (desc) before limiting
            required: false
            type: integer
        -   name: name_like
            in: query
            description: name regular expression
            required: false
            type: string
        -   name: cloud_resource_id_like
            in: query
            description: cloud_resource_id regular expression
            required: false
            type: string
        -   name: format
            in: query
            description: Output format
            required: false
            type: string
            default: advanced_json
            enum: [advanced_json, json, xlsx]
        -   name: traffic_from
            in: query
            description: >
                traffic_from filter in <region_name>:<cloud_type> format or 'ANY'
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: traffic_to
            in: query
            description: >
                traffic_to filter in <region_name>:<cloud_type> format or 'ANY'
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: field
            in: query
            description: >
                If provided, only specified fields will be set for expenses.
                Inner fields can be specified using dots. E.g. 'owner.id'.
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        responses:
            200:
                description: Clean expense data
                schema:
                    type: object
                    properties:
                        clean_expenses:
                            type: array
                            items:
                                type: object
                                properties:
                                    cloud_account_id:
                                        type: string
                                        description: cloud account id
                                        example: 060dccbf-616f-4bcf-b9d2-0ce9678454bc
                                    cloud_resource_id:
                                        type: string
                                        description: cloud-native resource id
                                        example: i-09dc9f5553f84a9ad
                                    active:
                                        type: boolean
                                        description: resource is discovered in cloud during the last discovery attempt
                                        example: true
                                    applied_rules:
                                        type: array
                                        description: Applied rules
                                        items:
                                            type: object
                                            properties:
                                                id:
                                                    type: string
                                                    description: Applied rule id
                                                    example: 128bdcc4-7c18-423a-a257-e1479aa0bd85
                                                name:
                                                    type: string
                                                    description: Applied rule name
                                                    example: Rule for AWS_1666950422
                                                pool_id:
                                                    type: string
                                                    description: Pool id
                                                    example: 4703dd9a-b3d2-437e-a63c-18b749edf2ca
                                            example:
                                                -   id: 128bdcc4-7c18-423a-a257-e1479aa0bd85
                                                    name: Rule for AWS_1666950422
                                                    pool_id: 4703dd9a-b3d2-437e-a63c-18b749edf2ca
                                                -   id: 31dc4700-2591-4c57-8bba-d1ae9b408df8
                                                    name: My rule
                                                    pool_id: 4703dd9a-b3d2-437e-a63c-18b749edf2ca
                                    cloud_created_at:
                                        type: integer
                                        description: created in cloud timestamp
                                        example: 1662978587
                                    created_at:
                                        type: integer
                                        description: discovered timestamp
                                        example: 1666950653
                                    deleted_at:
                                        type: integer
                                        description: deleted timestamp
                                        example: 0
                                    employee_id:
                                        type: string
                                        description: cloud resource owner id
                                        example: fdf1146f-5209-42f9-b946-ea6dcc9941e3
                                    first_seen:
                                        type: integer
                                        description: first appearance in timestamp
                                        example: 1662976800
                                    last_seen:
                                        type: integer
                                        description: last appearance timestamp
                                        example: 1667214000
                                    meta:
                                        type: object
                                        description: |
                                            flavor: t2.large
                                            spotted: False
                                            vpc_id: vpc-83d1f6e8
                                            os: Linux
                                    pool_id:
                                        type: string
                                        description: pool for resource
                                        example: 4703dd9a-b3d2-437e-a63c-18b749edf2ca
                                    region:
                                        type: string
                                        description: resource region
                                        example: eu-central-1
                                    resource_type:
                                        type: string
                                        description: resource type
                                        example: Instance
                                    tags:
                                        type: object
                                        description: resource's tags fields
                                        example:
                                            aws:createdBy: IAMUser:AKIDa:sd-iam-full
                                            mytag: myval
                                    has_metrics:
                                        type: boolean
                                        description: resource has usage metrics
                                        example: true
                                    service_name:
                                        type: string
                                        description: resource service name
                                        example: AmazonEC2
                                    last_expense:
                                        type: object
                                        description: Last expense information
                                        properties:
                                            date:
                                                type: integer
                                                description: date of last expense
                                                example: 1667174400
                                            cost:
                                                type: number
                                                description: cost of last expense
                                                example: 1.37
                                        example:
                                            date: 1667174400
                                            cost: 1.37
                                    total_cost:
                                        type: number
                                        description: cost for all time of existence
                                        example: 182.66
                                    id:
                                        type: string
                                        description: id of resource
                                        example: 245137c1-7605-4ae2-b8ef-ce0b4f979780
                                    is_environment:
                                        type: boolean
                                        description: resource has been created as environment
                                        example: false
                                    saving:
                                        type: number
                                        description: possible savings for resource
                                        example: 182.66
                                    cost:
                                        type: number
                                        description: cost for selected time interval
                                        example: 5.14
                                    cloud_account_name:
                                        type: string
                                        description: cloud account name
                                        example: AWS
                                    cloud_account_type:
                                        type: string
                                        description: cloud account type
                                        example: aws_cnr
                                    owner:
                                        type: object
                                        description:
                                        properties:
                                            id:
                                                type: string
                                                description: owner id
                                                example: fdf1146f-5209-42f9-b946-ea6dcc9941e3
                                            name:
                                                type: string
                                                description: owner name
                                                example: sd
                                        example:
                                            id: fdf1146f-5209-42f9-b946-ea6dcc9941e3
                                            name: sd
                                    pool:
                                        type:
                                        description:
                                        properties:
                                            id:
                                                type: string
                                                description: pool id
                                                example: 4703dd9a-b3d2-437e-a63c-18b749edf2ca
                                            name:
                                                type: string
                                                description: pool name
                                                example: AWS
                                            purpose:
                                                type: string
                                                description: pool purpose
                                                example: budget
                                        example:
                                            id: 4703dd9a-b3d2-437e-a63c-18b749edf2ca
                                            name: AWS
                                            purpose: budget
                                    resource_id:
                                        type: string
                                        description: resource id
                                        example: 245137c1-7605-4ae2-b8ef-ce0b4f979780
                                    resource_name:
                                        type: string
                                        description: resource name
                                        example: vl-arcee-debug
                                    shareable:
                                        type: boolean
                                        description: resource is marked as environment
                                        example: false
                                    constraint_violated:
                                        type: boolean
                                        description: resource has constraint violations
                                        example: true
                                    traffic_expenses:
                                        type: array
                                        description: Resource's traffic expenses
                                        items:
                                            type: object
                                            properties:
                                                from:
                                                    type: string
                                                    description: traffic from region
                                                    example: eu-central-1
                                                to:
                                                    type: string
                                                    description: traffic to region
                                                    example: eu-west-1
                                                usage:
                                                    type: number
                                                    description: usage in megabytes
                                                    example: 5.21
                                                cost:
                                                    type: number
                                                    description: traffic cost
                                                    example: 1.05
                                            example:
                                                -   from: eu-central-1
                                                    to: eu-west-1
                                                    usage: 5.21
                                                    cost: 1.05
                                                -   from: eu-central-1
                                                    to: us-east-1
                                                    usage: 0.11
                                                    cost: 0.03
                            example:
                            -   cloud_account_id:
                                    2329c0fb-8e09-432c-b985-f52d1ebe5e61
                                cloud_account_name: my cloud acc for aws
                                cloud_account_type: aws_cnr
                                created_at: 1504854859
                                deleted_at: 0
                                employee_id: 6dd09724-e9dd-4f01-b8aa-fcf101480f82
                                first_seen: 1504854869
                                last_seen: 1646452800
                                pool_id: 55d324ff-5117-4eac-98ed-9a0f12ae6538
                                last_expense:
                                    date: 1646438400
                                    cost: 0.3
                                total_cost: 372.29
                                is_environment: False
                                saving: 50
                                resource_id:
                                    a91572c2-8f0d-4311-b958-db12a6ad6b2f
                                resource_name: my resource
                                resource_type: Volume
                                raw_data_links: 2
                                service_name: AmazonEC2
                                cloud_resource_id:
                                    7b13beaa-4940-4d89-9145-058b56226f61
                                pool:
                                    id: 55d324ff-5117-4eac-98ed-9a0f12ae6538
                                    name: my pool
                                    purpose: pool
                                owner:
                                    id: 6dd09724-e9dd-4f01-b8aa-fcf101480f82
                                    name: employee_1
                                region: us-east
                                cost: 450
                                active: true
                                constraint_violated: true
                                created_by_kind: ReplicaSet (for kubernetes only)
                                created_by_name: kube-proxy (for kubernetes only)
                                k8s_namespace: default (for kubernetes only)
                                k8s_node: ubuntu (for kubernetes only)
                                k8s_service: kube-dns (for kubernetes only)
                                recommendations:
                                    run_timestamp: 1604854859
                                    modules:
                                        -   saving: 50,
                                            name: module1
                                        -   saving: 20,
                                            name: module2
                                tags:
                                    tag_name_3: tag_value_3
                                    tag_name_4: tag_value_4
                                traffic_expenses:
                                    -   from: region_1
                                        to: region_2
                                        usage: 3
                                        cost: 4
                                    -   from: region_1
                                        to: External
                                        usage: 2
                                        cost: 1
                            -   cloud_account_id:
                                    fe72d0c4-4f6e-4e02-968b-dc3e31714251
                                cloud_account_name: my cloud acc for azure
                                cloud_account_type: azure_cnr
                                created_at: 1504854859
                                deleted_at: 0
                                employee_id: 6dd09724-e9dd-4f01-b8aa-fcf101480f82
                                first_seen: 1504854869
                                last_seen: 1646452800
                                pool_id: 55d324ff-5117-4eac-98ed-9a0f12ae6538
                                last_expense:
                                    date: 1646438400
                                    cost: 0.5
                                total_cost: 352.29
                                is_environment: False
                                saving: 100
                                resource_id:
                                    daac2c83-9e59-4141-93c8-d50453bd995b
                                resource_name: my resource 2
                                resource_type: Snapshot
                                raw_data_links: 48
                                service_name: AmazonEC2
                                cloud_resource_id:
                                    e8f401b2-372f-4722-a3c9-f776cc92e7ce
                                pool:
                                    id: 55d324ff-5117-4eac-98ed-9a0f12ae6538
                                    name: my pool
                                    purpose: pool
                                owner:
                                    id: 6dd09724-e9dd-4f01-b8aa-fcf101480f82
                                    name: employee_1
                                region: us-east
                                cost: 450
                                active: false
                                constraint_violated: true
                                created_by_kind: ReplicaSet (for kubernetes only)
                                created_by_name: kube-proxy (for kubernetes only)
                                k8s_namespace: default (for kubernetes only)
                                k8s_node: ubuntu (for kubernetes only)
                                k8s_service: kube-dns (for kubernetes only)
                                shareable: true
                                recommendations:
                                    run_timestamp: 1604854829
                                    modules:
                                        -   saving: 100,
                                            name: module_name1
                                tags:
                                    tag_name_1: tag_value_1
                                    tag_name_2: tag_value_2
                        total_count:
                            type: integer
                            description: >
                                total count of resources matched before limit
                                applied
                            example: 10
                        total_cost:
                            type: number
                            description: >
                                total cost of resources matched before limit
                                applied
                            example: 34.421556461467894
                        start_date:
                            type: integer
                            description: >
                                start date (timestamp in seconds)
                            example: 1643673600
                        end_date:
                            type: integer
                            description: >
                                end date (timestamp in seconds)
                            example: 1643673600
                        limit:
                            type: integer
                            description: >
                                max objects amount (limit applied)
                            example: 5000
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0216: Argument is not provided
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer value
                    - OE0212: Unexpected parameters
                    - OE0446: "end_date" should be greater than "start_date"
                    - OE0473: Format is not allowed
                    - OE0499: Incorrect resource type identity
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
            424:
                description: |
                    Failed dependency:
                    - OE0445: Organization doesn't have any cloud accounts connected
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        args = self.get_expense_arguments()
        exp_format = args.pop('format', 'advanced_json')
        fields = args.pop('field', None)
        try:
            res = await run_task(self.controller.get, organization_id, **args)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(404, exc)
        self._respond_data(exp_format, res, fields)


class RawExpenseAsyncHandler(CleanExpenseAsyncHandler):
    expenses_key = 'raw_expenses'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_filters.clear()
        self.bool_filters.clear()
        self.str_filters = ['format']
        self.int_filters = ['limit']

    def _get_controller_class(self):
        return RawExpenseAsyncController

    async def get(self, resource_id, **url_params):
        """
        ---
        description: |
            Get raw expenses
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [expenses]
        summary: Get raw expenses
        parameters:
        -   name: resource_id
            in: path
            description: resource id
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
        -   name: limit
            in: query
            description: >
                Limit amount of expenses returned. Must be >0. Expenses will be
                sorted by cost (desc) before limiting
        -   name: format
            in: query
            description: Output format
            required: false
            type: string
            default: advanced_json
            enum: [advanced_json, json, xlsx]

        responses:
            200:
                description: Raw expenses data
                schema:
                    type: object
                    properties:
                        start_date:
                            type: integer
                            description: >
                                start date
                            example: 1646265600
                        end_date:
                            type: integer
                            description: >
                                end date
                            example: 1646469119
                        total_count:
                            type: integer
                            description: >
                                total count of resources matched before limit
                                applied
                            example: 10
                        total_cost:
                            type: number
                            description: >
                                total cost of resources matched
                            example: 10.0
                        limit:
                            type: integer
                            description: >
                                max objects amount (limit applied)
                            example: 5000
                        raw_expenses:
                            type: array
                            items:
                                type: object
                            example:
                            -   product/servicename:
                                    Amazon Elastic Compute Cloud
                                pricing/term: OnDemand
                                lineItem/BlendedCost: 0.0781439012
                                product/location: US East (N. Virginia)
                                lineItem/LineItemDescription: $0.05 per
                                    GB-Month of snapshot data stored - US East
                                cloud_account_id:
                                    31dc4700-2591-4c57-8bba-d1ae9b408df8
                                bill/BillingPeriodStartDate:
                                    2020-05-01T00:00:00Z
                                lineItem/BlendedRate: 0.0500000000
                                lineItem/UnblendedRate: 0.0500000000
                                lineItem/ResourceId:
                                    arn:aws:ec2:us-east-1:044478323321
                                lineItem/UsageAmount: 1.5628780242
                                bill/PayerAccountId: 044478323321
                                product/region: us-east-1
                                lineItem/CurrencyCode: USD
                                identity/LineItemId: hok77ifxcjxuidiqqctspf
                                    r4qonkk2ignggcaysxo4zvnwowwcrq
                                product/storageMedia: Amazon S3
                                product/ProductName: Amazon Elastic Compute
                                    Cloud
                                lineItem/UnblendedCost: 0.0781439012
                                lineItem/UsageEndDate: 2020-05-02T00:00:00Z
                                bill/BillingPeriodEndDate: 2020-06-01T00:00:00Z
                                bill/BillingEntity: AWS
                                product/servicecode: AmazonEC2
                                pricing/unit: GB-Mo
                                _id: 5eae09918ff6427234649fc1
                                product/sku: 7U7TWP44UP36AT3R
                                lineItem/ProductCode: AmazonEC2
                                lineItem/UsageAccountId: 044478323321
                                pricing/RateId: 1738012212
                                lineItem/UsageStartDate: 2020-05-01T23:00:00Z
                                lineItem/LegalEntity: Amazon Web Services, Inc.
                                product/productFamily: Storage Snapshot
                                lineItem/Operation: CreateSnapshot
                                product/locationType: AWS Region
                                lineItem/UsageType: EBS:SnapshotUsage
                                reservation/SubscriptionId: 2496477743
                                bill/BillType: Anniversary
                                pricing/publicOnDemandCost: 0.0781439012
                                product/usagetype: EBS:SnapshotUsage
                                pricing/currency: USD
                                pricing/publicOnDemandRate: 0.0500000000
                                lineItem/LineItemType: Usage
                                identity/TimeInterval: 2020-05-01T00:00:00Z/
                                    2020-05-02T00:00:00Z
                            -   lineItem/LegalEntity: Amazon Web Services, Inc.
                                bill/BillingPeriodEndDate: 2020-06-01T00:00:00Z
                                bill/PayerAccountId: 044478323321
                                product/servicename: AWS Pools
                                lineItem/UsageStartDate: 2020-05-10T23:00:00Z
                                product/usagetype: PoolsUsage
                                cloud_account_id:
                                    31dc4700-2591-4c57-8bba-d1ae9b408df8
                                pricing/unit: Pool-days
                                bill/BillingEntity: AWS
                                pricing/term: OnDemand
                                lineItem/BlendedRate: 0.0000000000
                                _id: 5eb9e7145da0cee46ba4ae29
                                lineItem/UnblendedRate: 0.0000000000
                                lineItem/UsageAccountId: 044478323321
                                product/ProductName: AWS Pools
                                lineItem/LineItemType: Usage
                                lineItem/BlendedCost: 0.0000000000
                                product/sku: T2UVJ9XYT52FBFAF
                                lineItem/UnblendedCost: 0.0000000000
                                lineItem/ProductCode: AWSPools
                                lineItem/CurrencyCode: USD
                                pricing/publicOnDemandRate: 0.0200000000
                                product/location: Any
                                identity/TimeInterval: 2020-05-10T00:00:00Z/
                                    2020-05-11T00:00:00Z
                                product/servicecode: AWSPools
                                lineItem/UsageAmount: 1.0000000000
                                pricing/RateId: 484687328
                                product/locationType: AWS Region
                                lineItem/UsageType: PoolsUsage
                                bill/BillingPeriodStartDate:
                                    2020-05-01T00:00:00Z
                                product/productFamily: AWS Pools
                                product/groupDescription: Pool Notifications
                                lineItem/LineItemDescription: $0.00 for 62
                                    Pool-days per month (free tier)
                                identity/LineItemId: 4da7tdvu2amvuxyqekns2
                                    yhqj35ytqflza6x4lmkzughavpvwala
                                lineItem/UsageEndDate: 2020-05-11T00:00:00Z
                                bill/BillType: Anniversary
                                lineItem/Operation: PoolsOperation
                                reservation/SubscriptionId: 1108502665
                                product/region: global
                                pricing/publicOnDemandCost: 0.0200000000
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0216: Argument is not provided
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer value
                    - OE0212: Unexpected parameters
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
            424:
                description: |
                    Failed dependency:
                    - OE0445: Organization doesn't have any cloud accounts connected
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'cloud_resource', resource_id)

        args = self.get_expense_arguments()
        exp_format = args.pop('format', 'advanced_json')
        try:
            res = await run_task(self.controller.get, resource_id, **args)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(404, exc)
        self._respond_data(exp_format, res)


class SummaryExpenseAsyncHandler(CleanExpenseAsyncHandler):
    expenses_key = 'summary_expenses'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.int_filters.remove('limit')
        self.list_filters.remove('field')

    def _get_controller_class(self):
        return SummaryExpenseAsyncController

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get expenses summary
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [expenses]
        summary: Get expenses summary
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
        -   name: cloud_account_id
            in: query
            description: cloud account id
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: pool_id
            in: query
            description: >
                handle pool id (and it's children if pool_id ends with a + sign)
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: owner_id
            in: query
            description: resource owner id
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: region
            in: query
            description: region
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: service_name
            in: query
            description: service_name
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: resource_type
            in: query
            description: >
                resource_type in format resource_type:type_resource_type.
                Supported type_resource_type values - [regular, cluster, environment]
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: active
            in: query
            description: Active
            required: false
            type: boolean
        -   name: recommendations
            in: query
            description: Recommendations
            required: false
            type: boolean
        -   name: constraint_violated
            in: query
            description: constraint_violated
            required: false
            type: boolean
        -   name: created_by_kind (for kubernetes only)
            in: query
            description: created_by_kind
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: created_by_name (for kubernetes only)
            in: query
            description: created_by_name
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: k8s_namespace (for kubernetes only)
            in: query
            description: k8s_namespace
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: k8s_node (for kubernetes only)
            in: query
            description: k8s_node
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: k8s_service (for kubernetes only)
            in: query
            description: k8s_service
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: tag
            in: query
            description: tag name
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: without_tag
            in: query
            description: tag name
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: name_like
            in: query
            description: name regular expression
            required: false
            type: string
        -   name: cloud_resource_id_like
            in: query
            description: cloud_resource_id regular expression
            required: false
            type: string
        -   name: format
            in: query
            description: Output format
            required: false
            type: string
            default: advanced_json
            enum: [advanced_json, json, xlsx]
        -   name: traffic_from
            in: query
            description: >
                traffic_from filter in <region_name>:<cloud_type> format or 'ANY'
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        -   name: traffic_to
            in: query
            description: >
                traffic_to filter in <region_name>:<cloud_type> format or 'ANY'
            required: false
            type: array
            collectionFormat: multi
            items:
                type: string
        responses:
            200:
                description: Summary expense data
                schema:
                    type: object
                    properties:
                        total_count:
                            type: integer
                            description: >
                                total count of resources matched before limit
                                applied
                            example: 10
                        total_cost:
                            type: number
                            description: >
                                total cost of resources matched before limit
                                applied
                            example: 34.421556461467894
                        total_saving:
                            type: number
                            description: >
                                total saving of resources matched before limit
                                applied
                            example: 12.614
                        start_date:
                            type: integer
                            description: >
                                start date (timestamp in seconds)
                            example: 1643673600
                        end_date:
                            type: integer
                            description: >
                                end date (timestamp in seconds)
                            example: 1643673600
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0216: Argument is not provided
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer value
                    - OE0212: Unexpected parameters
                    - OE0446: "end_date" should be greater than "start_date"
                    - OE0499: Incorrect resource type identity
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
            424:
                description: |
                    Failed dependency:
                    - OE0445: Organization doesn't have any cloud accounts connected
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('INFO_ORGANIZATION',
                                         'organization', organization_id)
        args = self.get_expense_arguments()
        exp_format = args.pop('format', 'advanced_json')
        try:
            res = await run_task(self.controller.get, organization_id, **args)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(404, exc)
        self._respond_data(exp_format, res)


class BreakdownExpensesBaseAsyncHandler(FilteredExpensesBaseAsyncHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.str_filters.append('breakdown_by')
        self.allowed_breakdowns = {
            'employee_id', 'pool_id', 'cloud_account_id',
            'service_name', 'region', 'resource_type',
            'k8s_node', 'k8s_namespace', 'k8s_service'
        }

    def get_expense_arguments(self, filter_required=True):
        args = super().get_expense_arguments()
        breakdown_by = self.get_arg('breakdown_by', str)
        if breakdown_by and breakdown_by not in self.allowed_breakdowns:
            raise OptHTTPError(400, Err.OE0217, ['breakdown_by'])
        return args
