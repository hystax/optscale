import json
from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            NotFoundException)
from optscale_exceptions.http_exc import OptHTTPError
from rest_api_server.controllers.organization_bi import (
    OrganizationBIAsyncController,
    BIAsyncController,
)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler,
    BaseAsyncItemHandler,
)
from rest_api_server.utils import (check_string, raise_unexpected_exception,
                                   check_int_attribute, raise_not_provided_exception,
                                   check_dict_attribute, ModelEncoder, run_task)


class OrganizationBIAsyncCollectionHandler(BaseAsyncCollectionHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return OrganizationBIAsyncController

    @property
    def _collection_get_key(self):
        return "organization_bis"

    def _validate_params(self, **kwargs):
        optional = ['name', 'days']
        required = ['organization_id', 'type', 'meta']
        try:
            args_unexpected = list(
                filter(lambda x: x not in required + optional, kwargs.keys()))
            if args_unexpected:
                raise_unexpected_exception(args_unexpected)
            args_missing = list(
                filter(lambda x: x not in kwargs.keys(), required))
            if args_missing:
                raise_not_provided_exception(args_missing)
            name = kwargs.get('name')
            if name is not None:
                check_string('name', name)
            days = kwargs.get('days')
            if days is not None:
                check_int_attribute('days', days)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create new organization BI subscription
            Required permission: EDIT_PARTNER
        summary: Create organization BI subscription
        tags: [organization_bi]
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Organization BI to add
            required: true
            schema:
                type: object
                properties:
                    type:
                        type: string
                        description: Type of BI
                        required: True
                        example: AWS_RAW_EXPORT
                        enum: [AWS_RAW_EXPORT, AZURE_RAW_EXPORT]
                    name:
                        type: string
                        description: |
                            Name for BI subscription. If not provided - name of
                            organization is taken by default.
                        required: False
                        example: "HystaxBI"
                    days:
                        type: integer
                        description: number of days for which to export data
                        required: false
                        default: 180
                        example: 30
                    meta:
                        type: object
                        description: "specific data for concrete BI type"
        responses:
            201:
                description: Success (returns created object)
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique organization BI id"}
                        organization_id: {type: string,
                            description: "Organization id of BI"}
                        name: {type: string,
                            description: "Name of BI"}
                        days: {type: integer,
                            description: "Number of days to export"}
                        deleted_at: {type: integer,
                            description: "Deleted timestamp (service field)"}
                        created_at: {type: integer,
                            description: "Creation timestamp (service field)"}
                        meta: {type: object,
                            description: "specific data for concrete BI type"}
                        type: {type: string,
                            description: "Type of target BI"}
                        status: {type: string,
                            description: "Current status of BI subscription"}
                        last_status_error: {type: string,
                            description: "Error message. Must be null in case
                            if 'status' is not FAILED"}
                        last_run: {type: integer,
                            description: "Timestamp of the last run"}
                        next_run: {type: integer,
                            description: "Timestamp for the next run"}
                        last_completed: {type: integer,
                            description: "Timestamp of the last run
                            successful run"}
                    example:
                        {
                        "deleted_at": 0,
                        "id": "fe5a82fa-bdfc-4be8-a7d8-bc5d52b58d91",
                        "meta": {
                          "access_key_id": "access_key_id",
                          "secret_access_key": "secret_access_key",
                          "bucket": "s3-bucket",
                          "s3_prefix": ""
                        },
                        "created_at": 1653895631,
                        "organization_id": "987f356e-9865-47be-a237-ebeb7b2227bd",
                        "type": "AWS_RAW_EXPORT",
                        "last_run": 0,
                        "next_run": 1653895631,
                        "last_completed": 0,
                        "status": "ACTIVE",
                        "last_status_error": null,
                        "name": "Hystax",
                        "days": 30,
                        }
            400:
                description: |
                    Wrong arguments:
                        - OE0149: OrganizationBI with name already exists
                        - OE0174: Type is invalid
                        - OE0212: Unexpected parameters
                        - OE0214: Argument should be a string
                        - OE0216: Argument is not provided
                        - OE0219: Invalid JSON body
                        - OE0223: should be integer
                        - OE0224: Invalid parameter value
                        - OE0546: Parameter is not supported for type
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                        - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
            424:
                description: |
                    Failed dependency:
                    - OE0523: last_status_error must be empty for SUCCESS/ACTIVE status
                    - OE0525: last_status_error must be not empty for FAILED status
        security:
        - token: []
        """
        await self.check_permissions('EDIT_PARTNER', 'organization',
                                     organization_id)
        await super().post(organization_id=organization_id, **url_params)

    async def get(self, organization_id, **url_params):
        """
            ---
            description: |
                Gets a list of all active Organization BI subscriptions.
                Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
            tags: [organization_bi]
            summary: List of BIs
            responses:
                200:
                    description: Organization BI list
                    schema:
                        type: object
                        properties:
                            organization_bis:
                                type: array
                                items:
                                    type: object
                                    properties:
                                        id: {type: string,
                                            description: "Unique organization BI id"}
                                        organization_id: {type: string,
                                            description: "Organization id of BI"}
                                        name: {type: string,
                                            description: "Name of BI"}
                                        days: {type: integer,
                                            description: "Number of days to export"}
                                        deleted_at: {type: integer,
                                            description: "Deleted timestamp (service field)"}
                                        created_at: {type: integer,
                                            description: "Creation timestamp (service field)"}
                                        meta: {type: object,
                                            description: "specific data for concrete BI type"}
                                        type: {type: string,
                                            description: "Type of target BI"}
                                        status: {type: string,
                                            description: "Current status of BI subscription"}
                                        last_status_error: {type: string,
                                            description: "Error message. Must be null in case
                                            if 'status' is not FAILED"}
                                        last_run: {type: integer,
                                            description: "Timestamp of the last run"}
                                        next_run: {type: integer,
                                            description: "Timestamp for the next run"}
                                        last_completed: {type: integer,
                                            description: "Timestamp of the last run
                                            successful run"}
                401:
                    description: |
                        Unauthorized:
                        - OE0235: Unauthorized
                        - OE0237: This resource requires authorization
                403: {description: "Forbidden: \n\n
                    - OE0236: Bad secret"}
            security:
                - token: []
                - secret: []
        """
        secure = False
        if not self.check_cluster_secret(raises=False):
            secure = True
            await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                         organization_id)
        res_ = await run_task(self.controller.list, organization_id, **url_params)
        res = {
            self._collection_get_key: [x.to_dict(secure=secure) for x in res_]
        }
        self.set_status(200)
        self.write(json.dumps(res, cls=ModelEncoder))


class BIAsyncCollectionHandler(OrganizationBIAsyncCollectionHandler):
    def _get_controller_class(self):
        return BIAsyncController

    async def post(self, **url_params):
        self.raise405()

    async def get(self, **url_params):
        """
            ---
            description: |
                Gets a list of all active Organization BI subscriptions (internal usage).
                Required permission: CLUSTER_SECRET
            tags: [organization_bi]
            summary: List of BIs
            responses:
                200:
                    description: Organization BI list
                    schema:
                        type: object
                        properties:
                            organization_bis:
                                type: array
                                items:
                                    type: object
                                    properties:
                                        id: {type: string,
                                            description: "Unique organization BI id"}
                                        organization_id: {type: string,
                                            description: "Organization id of BI"}
                                        name: {type: string,
                                            description: "Name of BI"}
                                        days: {type: integer,
                                            description: "Number of days to export"}
                                        deleted_at: {type: integer,
                                            description: "Deleted timestamp (service field)"}
                                        created_at: {type: integer,
                                            description: "Creation timestamp (service field)"}
                                        meta: {type: object,
                                            description: "specific data for concrete BI type"}
                                        type: {type: string,
                                            description: "Type of target BI"}
                                        status: {type: string,
                                            description: "Current status of BI subscription"}
                                        last_status_error: {type: string,
                                            description: "Error message. Must be null in case
                                            if 'status' is not FAILED"}
                                        last_run: {type: integer,
                                            description: "Timestamp of the last run"}
                                        next_run: {type: integer,
                                            description: "Timestamp for the next run"}
                                        last_completed: {type: integer,
                                            description: "Timestamp of the last run
                                            successful run"}
                401:
                    description: |
                        Unauthorized:
                        - OE0235: Unauthorized
                        - OE0237: This resource requires authorization
                403: {description: "Forbidden: \n\n
                    - OE0236: Bad secret"}
            security:
                - secret: []
        """
        self.check_cluster_secret()
        res_ = await run_task(self.controller.list, **url_params)
        res = {
            self._collection_get_key: [x.to_dict(secure=False) for x in res_]
        }
        self.set_status(200)
        self.write(json.dumps(res, cls=ModelEncoder))


class BIAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return BIAsyncController

    async def get(self, organization_bi_id):
        """
            ---
            description: |
                Gets Organization BI by id.
                Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
            tags: [organization_bi]
            summary: Gets organization BI by id
            parameters:
            -   name: organization_bi_id
                in: path
                description: Organization BI id
                required: true
                type: string
            responses:
                200:
                    description: Organization BI
                    schema:
                        type: object
                        properties:
                            id: {type: string,
                                description: "Unique organization BI id"}
                            organization_id: {type: string,
                                description: "Organization id of BI"}
                            name: {type: string,
                                description: "Name of BI"}
                            days: {type: integer,
                                description: "Number of days to export"}
                            deleted_at: {type: integer,
                                description: "Deleted timestamp (service field)"}
                            created_at: {type: integer,
                                description: "Creation timestamp (service field)"}
                            meta: {type: object,
                                description: "specific data for concrete BI type"}
                            type: {type: string,
                                description: "Type of target BI"}
                            status: {type: string,
                                description: "Current status of BI subscription"}
                            last_status_error: {type: string,
                                description: "Error message. Must be null in case
                                if 'status' is not FAILED"}
                            last_run: {type: integer,
                                description: "Timestamp of the last run"}
                            next_run: {type: integer,
                                description: "Timestamp for the next run"}
                            last_completed: {type: integer,
                                description: "Timestamp of the last run
                                successful run"}
                            files: {type: array, items: {type: string},
                                description: "List of exported file paths"}
                401:
                    description: |
                        Unauthorized:
                        - OE0235: Unauthorized
                        - OE0237: This resource requires authorization
                403: {description: "Forbidden: \n\n
                    - OE0236: Bad secret"}
                404: {description: "Not found: \n\n
                    - OE0002: Organization BI not found"}
            security:
            - token: []
            - secret: []
        """
        secure = False
        if not self.check_cluster_secret(raises=False):
            secure = True
            await self.check_permissions('INFO_ORGANIZATION', 'organization_bi',
                                         organization_bi_id)
        try:
            item = await self._get_item(organization_bi_id)
            self.write(item.to_json(secure, with_files=True))
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)

    @staticmethod
    def validate_params(**kwargs):
        int_params = ['last_run', 'last_completed', 'next_run', 'days']
        str_params = ['name', 'status', 'last_status_error']
        dict_params = ['meta']
        try:
            args_unexpected = list(filter(
                lambda x: x not in int_params + str_params + dict_params,
                kwargs.keys()))
            if args_unexpected:
                raise_unexpected_exception(args_unexpected)
            for param in str_params:
                if param in kwargs and kwargs[param]:
                    check_string(param, kwargs[param])
            for param in int_params:
                if param in kwargs and kwargs[param]:
                    check_int_attribute(param, kwargs[param])
            for param in dict_params:
                if param in kwargs and kwargs[param]:
                    check_dict_attribute(param, kwargs[param])
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)

    async def patch(self, organization_bi_id, **kwargs):
        """
            ---
            description: |
                Updates BI of the organizations.
                Required permission: CLUSTER_SECRET or EDIT_PARTNER
            tags: [organization_bi]
            summary: Updates organization BI
            parameters:
            -   name: organization_bi_id
                in: path
                description: Organization BI id
                required: true
                type: string
            -   in: body
                name: body
                description: Organization BI info to update
                required: false
                schema:
                    type: object
                    properties:
                        status:
                            type: string
                            description: Status of BI subscription
                            required: False
                            example: RUNNING
                            enum: [ACTIVE, QUEUED, RUNNING, FAILED, SUCCESS]
                        last_run:
                            type: integer
                            description: Timestamp of the last run
                            required: False
                            example: 3456543
                        next_run:
                            type: integer
                            description: Timestamp for the next run
                            required: False
                            example: 3456543
                        last_completed:
                            type: integer
                            description: Timestamp for the last successful run
                            required: False
                            example: 3456543
                        last_status_error:
                            type: string
                            description: |
                                Error for the last failed run, must be empty if
                                the last run was successful
                            required: False
                        name:
                            type: string
                            description: Name of BI
                            required: False
                        days:
                            type: integer
                            description: Number of days to export
                            required: False
                            example: 100
                        meta:
                            type: object
                            description: specific data for concrete BI type
                            required: False
            responses:
                200:
                    description: Organization BI
                    schema:
                        type: object
                        properties:
                            id: {type: string,
                                description: "Unique organization BI id"}
                            organization_id: {type: string,
                                description: "Organization id of BI"}
                            name: {type: string,
                                description: "Name of BI"}
                            days: {type: integer,
                                description: "Number of days to export"}
                            deleted_at: {type: integer,
                                description: "Deleted timestamp (service field)"}
                            created_at: {type: integer,
                                description: "Creation timestamp (service field)"}
                            meta: {type: object,
                                description: "specific data for concrete BI type"}
                            type: {type: string,
                                description: "Type of target BI"}
                            status: {type: string,
                                description: "Current status of BI subscription"}
                            last_status_error: {type: string,
                                description: "Error message. Must be null in case
                                if 'status' is not FAILED"}
                            last_run: {type: integer,
                                description: "Timestamp of the last run"}
                            next_run: {type: integer,
                                description: "Timestamp for the next run"}
                            last_completed: {type: integer,
                                description: "Timestamp of the last run
                                successful run"}
                400:
                    description: |
                        Wrong arguments:
                        - OE0149: OrganizationBI with name already exists
                        - OE0174: Type is invalid
                        - OE0211: Immutable parameters
                        - OE0212: Unexpected parameters
                        - OE0214: Argument should be a string
                        - OE0215: Wrong argument's length
                        - OE0216: Argument is not provided
                        - OE0219: Invalid JSON body
                        - OE0223: should be integer
                        - OE0224: Invalid parameter value
                        - OE0525: last_error_code must be not empty for FAILED status
                        - OE0546: Parameter is not supported for type
                401:
                    description: |
                        Unauthorized:
                        - OE0235: Unauthorized
                        - OE0237: This resource requires authorization
                403: {description: "Forbidden: \n\n
                    - OE0236: Bad secret"}
                404: {description: "Not found: \n\n
                    - OE0002: Organization BI not found"}
                424:
                    description: |
                        Failed dependency:
                        - OE0523: last_status_error must be empty for SUCCESS/ACTIVE status
                        - OE0525: last_status_error must be not empty for FAILED status
            security:
            - token: []
            - secret: []
        """
        secure = False
        if not self.check_cluster_secret(raises=False):
            secure = True
            await self.check_permissions('EDIT_PARTNER', 'organization_bi',
                                         organization_bi_id)
        try:
            await self._get_item(organization_bi_id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        data = self._request_body()
        self.validate_params(**data)
        res = await run_task(self.controller.edit, organization_bi_id, **data)
        self.write(res.to_json(secure=secure))

    async def delete(self, organization_bi_id, **kwargs):
        """
            ---
            description: |
                Deletes organization BI with specified id
                Required permission: EDIT_PARTNER
            tags: [organization_bi]
            summary: Delete organization BI
            parameters:
            -   name: organization_bi_id
                in: path
                description: Organization BI id
                required: true
                type: string
            responses:
                204:
                    description: Success
                401:
                    description: |
                        Unauthorized:
                        - OE0235: Unauthorized
                        - OE0237: This resource requires authorization
                404:
                    description: |
                        Not found:
                        - OE0002: OrganizationBI not found
                403:
                    description: |
                        Forbidden:
                            - OE0236: Bad secret
            security:
            - token: []
        """
        await self.check_permissions('EDIT_PARTNER', 'organization_bi',
                                     organization_bi_id)
        await run_task(self.controller.delete, organization_bi_id, **kwargs)
        self.set_status(204)
