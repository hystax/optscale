import json
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.iostream import StreamClosedError
from rest_api.rest_api_server.controllers.organization_gemini import (
    GeminiAsyncController, GeminiDataAsyncController,
    OrganizationGeminiAsyncController
)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.handlers.v1.base_async import BaseAsyncItemHandler, BaseAsyncCollectionHandler
from rest_api.rest_api_server.utils import (
    ModelEncoder, run_task, check_list_attribute, check_string_attribute
)
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException


class GeminisAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return GeminiAsyncController

    async def get(self, gemini_id):
        """
            ---
            description: |
                Gets gemini by id.
                Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
            tags: [gemini]
            summary: Gets gemini by id
            parameters:
            -   name: gemini_id
                in: path
                description: Gemini id
                required: true
                type: string
            responses:
                200:
                    description: Gemini
                    schema:
                        type: object
                        properties:
                            id: {type: string,
                                description: "Unique organization gemini id"}
                            organization_id: {type: string,
                                description: "Organization id of gemini"}
                            deleted_at: {type: string,
                                description: "Deleted timestamp (service field)"}
                            created_at: {type: string,
                                description: "Creation timestamp (service field)"}
                            filters: {type: object,
                                description: "Specific filters for checking duplicates"}
                            status: {type: string,
                                description: "Current status of gemini check"}
                            stats:
                                type: object
                                description: "Statistics of gemini check"
                                properties:
                                    total_objects:
                                        type: integer
                                        description: Total object count
                                    filtered_objects:
                                        type: integer
                                        description: Filtered object count
                                    total_size:
                                        type: integer
                                        description: Total size
                                    duplicates_size:
                                        type: integer
                                        description: Duplicates size
                                    duplicated_objects:
                                        type: integer
                                        description: Duplicated objects count
                                    monthly_savings:
                                        type: integer
                                        description: Monthly savings for deleting duplicates
                                    buckets:
                                        type: object
                                        properties:
                                            bucket:
                                                type: object
                                                description: Bucket name
                                                properties:
                                                    total_objects:
                                                        type: integer
                                                        description: Total object count
                                                    filtered_objects:
                                                        type: integer
                                                        description: Filtered object count
                                                    size:
                                                        type: integer
                                                        description: Bucket size
                                                    monthly_cost:
                                                        type: number
                                                        description: Bucket storage monthly cost
                                    matrix:
                                        type: object
                                        description: Cross-bucket duplicates matrix
                            last_error: {type: string,
                                description: "Error message. Must be null in case
                                if 'status' is not FAILED"}
                            last_run: {type: integer,
                                description: "Timestamp of the last run"}
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
                404: {description: "Not found: \n\n
                    - OE0002: Gemini not found"}
            security:
            - token: []
            - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization_gemini', gemini_id)
        await super().get(gemini_id)

    async def patch(self, gemini_id, **kwargs):
        """
            ---
            description: |
                Updates Gemini of the organizations.
                Required permission: CLUSTER_SECRET or EDIT_PARTNER
            tags: [gemini]
            summary: Updates organization gemini
            parameters:
            -   name: gemini_id
                in: path
                description: Gemini id
                required: true
                type: string
            -   in: body
                name: body
                description: Gemini info to update
                required: true
                schema:
                    type: object
                    properties:
                        status:
                            type: string
                            description: Status of gemini run
                            required: False
                            example: RUNNING
                            enum: [CREATED, RUNNING, FAILED, SUCCESS]
                        last_run:
                            type: integer
                            description: Timestamp of the last run
                            required: False
                            example: 3456543
                        last_completed:
                            type: integer
                            description: Timestamp for the last successful run
                            required: False
                            example: 3456543
                        last_error:
                            type: string
                            description: Error for the last failed run, must be empty if the last run was successful
                            required: False
            responses:
                200:
                    description: Gemini
                    schema:
                        type: object
                        properties:
                            id: {type: string,
                                description: "Unique organization gemini id"}
                            organization_id: {type: string,
                                description: "Organization id of gemini"}
                            deleted_at: {type: string,
                                description: "Deleted timestamp (service field)"}
                            created_at: {type: string,
                                description: "Creation timestamp (service field)"}
                            filters: {type: object,
                                description: "Specific filters for checking duplicates"}
                            status: {type: string,
                                description: "Current status of gemini check"}
                            stats:
                                type: object
                                description: "Statistics of gemini check"
                                properties:
                                    total_objects:
                                        type: integer
                                        description: Total object count
                                    filtered_objects:
                                        type: integer
                                        description: Filtered object count
                                    total_size:
                                        type: integer
                                        description: Total size
                                    duplicates_size:
                                        type: integer
                                        description: Duplicates size
                                    duplicated_objects:
                                        type: integer
                                        description: Duplicated objects count
                                    monthly_savings:
                                        type: integer
                                        description: Monthly savings for deleting duplicates
                                    buckets:
                                        type: object
                                        properties:
                                            bucket:
                                                type: object
                                                description: Bucket name
                                                properties:
                                                    total_objects:
                                                        type: integer
                                                        description: Total object count
                                                    filtered_objects:
                                                        type: integer
                                                        description: Filtered object count
                                                    size:
                                                        type: integer
                                                        description: Bucket size
                                                    monthly_cost:
                                                        type: number
                                                        description: Bucket storage monthly cost
                                    matrix:
                                        type: object
                                        description: Cross-bucket duplicates matrix
                            last_error: {type: string,
                                description: "Error message. Must be null in case
                                if 'status' is not FAILED"}
                            last_run: {type: integer,
                                description: "Timestamp of the last run"}
                            last_completed: {type: integer,
                                description: "Timestamp of the last run
                                successful run"}
                400:
                    description: |
                        Wrong arguments:
                        - OE0223: Argument should be integer
                        - OE0466: Argument should be float
                401:
                    description: |
                        Unauthorized:
                        - OE0235: Unauthorized
                        - OE0237: This resource requires authorization
                403: {description: "Forbidden: \n\n
                    - OE0236: Bad secret"}
                404: {description: "Not found: \n\n
                    - OE0002: Gemini not found"}
                424:
                    description: |
                        Failed dependency:
                        - OE0523: last_error must be empty for SUCCESS/ACTIVE status
                        - OE0525: last_error must be not empty for FAILED status
            security:
            - token: []
            - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'EDIT_PARTNER', 'organization_gemini', gemini_id)
        data = self._request_body()
        res = await run_task(self.controller.edit, gemini_id, **data)
        self.write(res.to_json())

    async def delete(self, gemini_id, **kwargs):
        """
            ---
            description: |
                Deletes gemini with specified id
                Required permission: EDIT_PARTNER
            tags: [gemini]
            summary: Delete gemini
            parameters:
            -   name: gemini_id
                in: path
                description: Gemini id
                required: true
                type: string
            responses:
                204:
                    description: Success
                401:
                    description: |
                        Unauthorized:
                        - OE0235: Unauthorized
                404:
                    description: |
                        Not found:
                        - OE0002: Gemini not found
                403:
                    description: |
                        Forbidden:
                        - OE0234: Forbidden
            security:
            - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization_gemini', gemini_id)
        await run_task(self.controller.delete, gemini_id, **kwargs)
        self.set_status(204)


class GeminisAsyncCollectionHandler(BaseAsyncCollectionHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return OrganizationGeminiAsyncController

    async def post(self, **kwargs):
        self.raise405()

    async def get(self, **kwargs):
        """
            ---
            description: |
                Gets a list of all non-deleted geminis (internal usage).
                Required permission: CLUSTER_SECRET
            tags: [gemini]
            summary: List of geminis
            responses:
                200:
                    description: Organization geminis
                    schema:
                        type: object
                        properties:
                            geminis:
                                type: array
                                items:
                                    type: object
                                    properties:
                                        id: {type: string,
                                            description: "Unique organization gemini id"}
                                        organization_id: {type: string,
                                            description: "Organization id"}
                                        deleted_at: {type: string,
                                            description: "Deleted timestamp (service field)"}
                                        created_at: {type: string,
                                            description: "Creation timestamp (service field)"}
                                        filters: {type: object,
                                            description: "Specific filters for checking duplicates"}
                                        status: {type: string,
                                            description: "Current status of gemini check"}
                                        stats:
                                            type: object
                                            description: "Statistics of gemini check"
                                            properties:
                                                total_objects:
                                                    type: integer
                                                    description: Total object count
                                                filtered_objects:
                                                    type: integer
                                                    description: Filtered object count
                                                total_size:
                                                    type: integer
                                                    description: Total size
                                                duplicates_size:
                                                    type: integer
                                                    description: Duplicates size
                                                duplicated_objects:
                                                    type: integer
                                                    description: Duplicated objects count
                                                monthly_savings:
                                                    type: integer
                                                    description: Monthly savings for deleting duplicates
                                                buckets:
                                                    type: object
                                                    properties:
                                                        bucket:
                                                            type: object
                                                            description: Bucket name
                                                            properties:
                                                                total_objects:
                                                                    type: integer
                                                                    description: Total object count
                                                                filtered_objects:
                                                                    type: integer
                                                                    description: Filtered object count
                                                                size:
                                                                    type: integer
                                                                    description: Bucket size
                                                                monthly_cost:
                                                                    type: number
                                                                    description: Bucket storage monthly cost
                                                matrix:
                                                    type: object
                                                    description: Cross-bucket duplicates matrix
                                        last_error: {type: string,
                                            description: "Error message. Must be null in case
                                            if 'status' is not FAILED"}
                                        last_run: {type: integer,
                                            description: "Timestamp of the last run"}
                                        last_completed: {type: integer,
                                            description: "Timestamp of the last run
                                            successful run"}
                401:
                    description: |
                        Unauthorized:
                        - OE0235: Unauthorized
                403: {description: "Forbidden: \n\n
                    - OE0236: Bad secret"}
            security:
                - token: []
                - secret: []
        """

        self.check_cluster_secret()
        result = await run_task(self.controller.list, **kwargs)
        geminis = {"geminis": [
            gemini.to_dict() for gemini in result
        ]}
        self.write(json.dumps(geminis, cls=ModelEncoder))


class OrganizationGeminisAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                                BaseAuthHandler):
    def _get_controller_class(self):
        return OrganizationGeminiAsyncController

    async def post(self, organization_id, **kwargs):
        """
        ---
        description: |
            Creates new organization gemini
            Required permission: EDIT_PARTNER
        summary: Creates organization gemini
        tags: [gemini]
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Organization gemini to add
            required: true
            schema:
                type: object
                properties:
                    filters:
                        type: object
                        description: "Specific filters for checking duplicates"
        responses:
            201:
                description: Success (returns created object)
                schema:
                    type: object
                    properties:
                        id: {type: string,
                            description: "Unique organization gemini id"}
                        organization_id: {type: string,
                            description: "Organization id of gemini"}
                        deleted_at: {type: string,
                            description: "Deleted timestamp (service field)"}
                        created_at: {type: string,
                            description: "Creation timestamp (service field)"}
                        filters: {type: object,
                            description: "Specific filters for checking duplicates"}
                        status: {type: string,
                            description: "Current status of gemini check"}
                        stats: {type: string,
                            description: "Statistics of gemini check"}
                        last_error: {type: string,
                            description: "Error message. Must be null in case
                            if 'status' is not FAILED"}
                        last_run: {type: integer,
                            description: "Timestamp of the last run"}
                        last_completed: {type: integer,
                            description: "Timestamp of the last run
                            successful run"}
                    example:
                        {
                        "deleted_at": 0,
                        "id": "fe5a82fa-bdfc-4be8-a7d8-bc5d52b58d91",
                        "filters": {
                          "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
                          "buckets": "bucket1,bucket2",
                          "min_size": 1,
                        },
                        "created_at": 1653895631,
                        "organization_id": "987f356e-9865-47be-a237-ebeb7b2227bd",
                        "last_run": 0,
                        "last_completed": 0,
                        "status": "ACTIVE",
                        "last_error": null,
                        }
            400:
                description: |
                    Wrong arguments
                    - OE0214: Argument should be a string
                    - OE0217: Invalid query parameter
                    - OE0223: min_size should be integer
                    - OE0385: buckets should be a list
            401:
                description: |
                    Unauthorized
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                        - OE0236: Bad secret
        security:
        - token: []
        """

        await self.check_permissions('EDIT_PARTNER', 'organization',
                                     organization_id)
        data = self._request_body()
        filters = data.get("filters", {})
        res = await run_task(self.controller.create,
                             organization_id=organization_id,
                             filters=filters)
        self.set_status(201)
        self.write(res.to_json())

    async def get(self, organization_id, **kwargs):
        """
            ---
            description: |
                Gets a list of all non-deleted organization geminis.
                Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
            tags: [gemini]
            summary: List of organization geminis
            parameters:
            -   name: organization_id
                in: path
                description: Organization id
                required: true
                type: string
            responses:
                200:
                    description: Organization geminis
                    schema:
                        type: object
                        properties:
                            geminis:
                                type: array
                                items:
                                    type: object
                                    properties:
                                        id: {type: string,
                                            description: "Unique organization gemini id"}
                                        organization_id: {type: string,
                                            description: "Organization id"}
                                        deleted_at: {type: string,
                                            description: "Deleted timestamp (service field)"}
                                        created_at: {type: string,
                                            description: "Creation timestamp (service field)"}
                                        filters: {type: object,
                                            description: "Specific filters for checking duplicates"}
                                        status: {type: string,
                                            description: "Current status of gemini check"}
                                        stats: {type: string,
                                            description: "Statistics of gemini check"}
                                        last_error: {type: string,
                                            description: "Error message. Must be null in case
                                            if 'status' is not FAILED"}
                                        last_run: {type: integer,
                                            description: "Timestamp of the last run"}
                                        last_completed: {type: integer,
                                            description: "Timestamp of the last run
                                            successful run"}
                401:
                    description: |
                        Unauthorized:
                        - OE0235: Unauthorized
                403: {description: "Forbidden: \n\n
                    - OE0236: Bad secret"}
            security:
                - token: []
                - secret: []
        """

        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                         organization_id)
        result = await run_task(self.controller.list, organization_id, **kwargs)
        geminis = {'geminis': [
            gemini.to_dict() for gemini in result
        ]}
        self.write(json.dumps(geminis, cls=ModelEncoder))


class GeminisDataAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                        BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return GeminiDataAsyncController

    def _validate_params(self, **kwargs):
        expected_params = ['buckets']
        unexpected = list(
            filter(lambda x: x not in expected_params, kwargs.keys()))
        if unexpected:
            message = ', '.join(unexpected)
            raise OptHTTPError(400, Err.OE0212, [message])
        try:
            buckets = kwargs.get('buckets')
            try:
                check_list_attribute('buckets', buckets)
                for bucket in buckets:
                    check_string_attribute('bucket', bucket)
                if len(buckets) > 2:
                    raise WrongArgumentsException(
                        Err.OE0224, ['buckets', 1, 2])
            except WrongArgumentsException as ex:
                raise OptHTTPError.from_opt_exception(400, ex)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        super()._validate_params(**kwargs)

    async def post(self, gemini_id, **kwargs):
        """
        ---
        description: |
            Creates gemini data processing task
            Required permission: CLUSTER_SECRET or EDIT_PARTNER
        tags: [gemini_data]
        summary: Creates gemini data
        parameters:
        -   name: gemini_id
            in: path
            description: Gemini id
            required: true
            type: string
        -   name: buckets
            in: body
            description: bucket names
            required: true
            type: array
            collectionFormat: multi
            items:
                type: string
        responses:
            200:
                description: Gemini data information
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Gemini data id
                        created_at:
                            type: integer
                            description: Created timestamp (service field)
                        deleted_at:
                            type: integer
                            description: Created timestamp (service field)
                        gemini_id:
                            type: string
                            description: Gemini id
                        buckets:
                            type: string
                            description: separated buckets string
                        status:
                            type: string
                            description: Gemini data processing status
                        url:
                            type: string
                            description: Download url
                        valid_until:
                            type: integer
                            description: Url valid until timestamp
            400:
                description: |
                    Wrong arguments:
                    - OE0211: Parameter is immutable
                    - OE0212: Unexpected parameters
                    - OE0216: Argument is not provided
                    - OE0224: Invalid buckets length
                    - OE0214: Argument should be a string
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
            409:
                description: |
                    Conflict:
                    - OE0551: Gemini data already exists
            424:
                description: |
                    Failed Dependency:
                    - OE0572: Invalid gemini status
        security:
        - token: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'EDIT_PARTNER', 'organization_gemini', gemini_id)
        data = self._request_body()
        self._validate_params(**data)
        buckets = data.get("buckets", {})
        result = await run_task(self.controller.create, gemini_id, buckets)
        self.write(json.dumps(result.to_dict(), cls=ModelEncoder))
        self.set_status(201)

    async def get(self, gemini_id, **kwargs):
        """
        ---
        description: |
            Gets a list of all non-deleted organization geminis.
            Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
        tags: [gemini_data]
        summary: List of organization geminis data
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   name: only_active
            in: query
            description: show with not expired valid_until
            required: false
            type: boolean
            default: false
        responses:
            200:
                description: Organization geminis data
                schema:
                    type: object
                    properties:
                        geminis_data:
                            type: array
                            items:
                                type: object
                                properties:
                                    id:
                                        type: string
                                        description: Gemini data id
                                    created_at:
                                        type: integer
                                        description: Created timestamp (service field)
                                    deleted_at:
                                        type: integer
                                        description: Created timestamp (service field)
                                    gemini_id:
                                        type: string
                                        description: Gemini id
                                    buckets:
                                        type: string
                                        description: separated buckets string
                                    status:
                                        type: string
                                        description: Gemini data processing status
                                    url:
                                        type: string
                                        description: Download url
                                    valid_until:
                                        type: integer
                                        description: Url valid until timestamp
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
        security:
            - token: []
            - secret: []
        """

        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization_gemini', gemini_id)
        only_active = self.get_arg('only_active', bool, False)
        result = await run_task(self.controller.list, gemini_id,
                                only_active=only_active, **kwargs)
        geminis = {'geminis_data': [
            gemini.to_dict() for gemini in result
        ]}
        self.write(json.dumps(geminis, cls=ModelEncoder))


class GeminisDataAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return GeminiDataAsyncController

    async def patch(self, gemini_data_id, **kwargs):
        """
        ---
        description: |
            Updates Gemini data.
            Required permission: CLUSTER_SECRET
        tags: [gemini_data]
        summary: Updates organization gemini data
        parameters:
        -   name: gemini_data_id
            in: path
            description: Gemini data id
            required: true
            type: string
        -   in: body
            name: body
            description: Gemini data info to update
            required: true
            schema:
                type: object
                properties:
                    status:
                        type: string
                        description: Status of gemini data generation task
                        required: False
                        example: RUNNING
                        enum: [QUEUED, RUNNING, FAILED, SUCCESS]
                    valid_until:
                        type: integer
                        description: URL valid until timestamp
                        required: False
                        required: False
                        example: 3456543
                    url:
                        type: string
                        description: Download url
                        required: False
        responses:
            200:
                description: Gemini
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Gemini data id
                        created_at:
                            type: integer
                            description: Created timestamp (service field)
                        deleted_at:
                            type: integer
                            description: Created timestamp (service field)
                        gemini_id:
                            type: string
                            description: Gemini id
                        buckets:
                            type: string
                            description: separated buckets string
                        status:
                            type: string
                            description: Gemini data processing status
                        url:
                            type: string
                            description: Download url
                        valid_until:
                            type: integer
                            description: Url valid until timestamp
            400:
                description: |
                    Wrong arguments:
                    - OE0223: Argument should be integer
                    - OE0466: Argument should be string
                    - OE0211: Parameter is immutable
                    - OE0212: Unexpected parameters
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403: {description: "Forbidden: \n\n
                - OE0236: Bad secret"}
            404: {description: "Not found: \n\n
                - OE0002: Gemini not found"}
        security:
        - token: []
        - secret: []
        """
        self.check_cluster_secret()
        data = self._request_body()
        res = await run_task(
            self.controller.edit, gemini_data_id, **data)
        if not res:
            type_name = self.controller.model_type.__name__
            raise OptHTTPError(404, Err.OE0002,
                               [type_name, gemini_data_id])
        self.write(json.dumps(res.to_dict(), cls=ModelEncoder))

    async def delete(self, **kwargs):
        self.raise405()

    async def get(self, gemini_data_id):
        """
        ---
        description: |
            Gets gemini data information
            Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
        tags: [gemini_data]
        summary: Gets gemini by id
        parameters:
        -   name: gemini_data_id
            in: path
            description: Gemini data id
            required: true
            type: string
        responses:
            200:
                description: Gemini data information
                schema:
                    type: object
                    properties:
                        id:
                            type: string
                            description: Gemini data id
                        created_at:
                            type: integer
                            description: Created timestamp (service field)
                        deleted_at:
                            type: integer
                            description: Created timestamp (service field)
                        gemini_id:
                            type: string
                            description: Gemini id
                        buckets:
                            type: string
                            description: separated buckets string
                        status:
                            type: string
                            description: Gemini data processing status
                        url:
                            type: string
                            description: Download url
                        valid_until:
                            type: integer
                            description: Url valid until timestamp
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
            424:
                description: |
                    Failed Dependency:
                    - OE0572: Invalid gemini status
        security:
        - token: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'gemini_data', gemini_data_id)
        result = await run_task(self.controller.get, gemini_data_id)
        self.write(json.dumps(result.to_dict(), cls=ModelEncoder))


class GeminiDataDownloadHandler(GeminisDataAsyncItemHandler):

    async def patch(self, gemini_data_id, **kwargs):
        self.raise405()

    async def get(self, gemini_data_id):
        """
        ---
        description: |
            Downloads gemini data
            Required permission: CLUSTER_SECRET or INFO_ORGANIZATION
        tags: [gemini_data_download]
        summary: Gets gemini by id
        parameters:
        -   name: gemini_data_id
            in: path
            description: Gemini data id
            required: true
            type: string
        responses:
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Object not found
            424:
                description: |
                    Failed Dependency:
                    - OE0572: Invalid gemini status
            502:
                description: |
                    Bad Gateway
            500:
                description: |
                    Internal Server Error
        security:
        - token: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'gemini_data', gemini_data_id)
        download_url = await run_task(
            self.controller.get_download_url, gemini_data_id)
        client = AsyncHTTPClient()
        range_header = self.request.headers.get("Range")
        headers = {"Range": range_header} if range_header else {}

        def header_callback(line: str):
            line = line.strip()
            if not line:
                return
            if line.startswith("HTTP/"):
                self.set_status(int(line.split(" ")[1]))
                return
            if ":" in line:
                key, value = map(str.strip, line.split(":", 1))
                if key in {
                    "Content-Type", "Content-Length", "Content-Disposition",
                    "Content-Range", "Accept-Ranges"
                }:
                    self.set_header(key, value)

        def streaming_callback(chunk: bytes):
            try:
                self.write(chunk)
                self.flush()
            except StreamClosedError:
                pass

        request = HTTPRequest(
            url=download_url,
            method="GET",
            headers=headers,
            header_callback=header_callback,
            streaming_callback=streaming_callback,
            request_timeout=0
        )

        try:
            response = await client.fetch(request, raise_error=False)
            if response.error and not self._finished:
                self.set_status(502)
                await self.finish()
        except StreamClosedError:
            pass
        except Exception:
            if not self._finished:
                self.set_status(500)
        finally:
            if not self._finished:
                await self.finish()
