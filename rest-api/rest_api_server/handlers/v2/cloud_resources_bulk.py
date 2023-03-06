import json
from optscale_exceptions.http_exc import OptHTTPError
from rest_api_server.controllers.cloud_resource import (
    CloudResourceAsyncController)
from rest_api_server.exceptions import Err
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.utils import run_task, ModelEncoder


class CloudResourceAsyncBulkCollectionHandler(BaseAsyncCollectionHandler,
                                              BaseAuthHandler, BaseHandler):
    def _get_controller_class(self):
        return CloudResourceAsyncController

    async def post(self, cloud_account_id, **kwargs):
        """
        ---
        description: |
            Bulk create cloud resources for specified cloud account
            Required permission: CLUSTER_SECRET
        tags: [cloud_resources]
        summary: Bulk create cloud resources for specified cloud account
        parameters:
        -   name: cloud_account_id
            in: path
            description: Cloud account id
            required: true
            type: string
        -   name: behavior
            in: query
            description: >
                API behavior, it can be one of the following:\n\n
                - 'error_existing' - fail if some resource already exists.
                It is the default behavior\n\n
                - 'skip_existing' - skip resources that already exist.
                They are still fetched and returned if return_resources=true\n\n
                - 'update_existing' - update resources that already exist.
                They are still fetched and returned if return_resources=true\n\n
            type: string
            enum: [error_existing, skip_existing, update_existing]
        -   name: return_resources
            in: query
            description: Whether to return resource data. Default is false.
            type: boolean
        -   name: is_report_import
            in: query
            description: Whether resource creation is initiated by report import process. Default is false.
            type: boolean
        -   in: body
            name: body
            description: Cloud resources to add
            required: true
            schema:
                type: object
                required: [resources]
                additionalProperties: false
                properties:
                    resources:
                        type: array
                        items:
                            type: object
                            required: [name, cloud_resource_id, resource_type]
                            additionalProperties: false
                            properties:
                                name: {type: string,
                                    description: "Cloud resource name"}
                                cloud_resource_id: {type: string,
                                    description: "Resource id in cloud"}
                                cloud_resource_hash: {type: string,
                                    description: "Resource hash in cloud"}
                                resource_type: {type: string,
                                    description: "Type of cloud resource"}
                                pool_id: {type: string,
                                    description: "Pool for resource"}
                                employee_id: {type: string,
                                    description: "Cloud resource owner id"}
                                tags: {type: object,
                                    description: "Cloud resource tags in name: value format"}
                                region: {type: string,
                                    description: "Cloud resource region"}
                                meta: {type: object,
                                    description: "resource's meta fields",
                                    example: {"preinstalled": "NA"}}
        responses:
            200:
                description: Resources data (if return_resources=true)
            204:
                description: Success (if return_resources=false)
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
                    - OE0426: Request body should be a dictionary
                    - OE0385: "resources" should be a list
                    - OE0212: Unexpected parameters
                    - OE0003: Database error
                    - OE0216: Argument is not provided
                    - OE0214: Argument should be a string
                    - OE0215: Wrong number of characters
                    - OE0219: Argument should be a string with valid JSON
                    - OE0456: Duplicate path parameters in the request body
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
            404:
                description: |
                    Not found:
                    - OE0002: Cloud account not found
        security:
        - secret: []
        """
        self.check_cluster_secret()

        behavior = self.get_arg('behavior', str, 'error_existing')
        if behavior not in ['error_existing', 'skip_existing',
                            'update_existing']:
            raise OptHTTPError(400, Err.OE0425, [behavior])

        return_resources = self.get_arg('return_resources', bool, False)
        is_report_import = self.get_arg('is_report_import', bool, False)

        data = self._request_body()
        if not isinstance(data, dict):
            raise OptHTTPError(400, Err.OE0426, [])

        resources = data.pop('resources', None)
        if resources is None:
            raise OptHTTPError(400, Err.OE0216, ['resources'])
        elif not isinstance(resources, list):
            raise OptHTTPError(400, Err.OE0385, ['resources'])

        if data:
            err_args = ','.join(data.keys())
            raise OptHTTPError(400, Err.OE0212, [err_args])

        res = await run_task(
            self.controller.save_bulk,
            cloud_account_id=cloud_account_id,
            resources=resources,
            behavior=behavior,
            return_resources=return_resources,
            is_report_import=is_report_import
        )
        if return_resources:
            self.set_status(200)
            resources_dict = {'resources': res}
            self.write(json.dumps(resources_dict, cls=ModelEncoder))
        else:
            self.set_status(204)
