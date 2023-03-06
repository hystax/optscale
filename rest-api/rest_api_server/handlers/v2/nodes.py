import json

from rest_api_server.controllers.node import NodesAsyncController
from rest_api_server.exceptions import Err
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v1.base_async import BaseAsyncCollectionHandler
from rest_api_server.utils import run_task, ModelEncoder

from optscale_exceptions.http_exc import OptHTTPError


class NodesAsyncCollectionBulkHandler(BaseAsyncCollectionHandler,
                                      BaseAuthHandler):
    def _get_controller_class(self):
        return NodesAsyncController

    async def post(self, cloud_account_id, **url_params):
        """
        ---
        description: |
            Bulk create nodes
            Required permission: CLUSTER_SECRET
        tags: [nodes]
        summary: Create cloud account nodes in one bulk operation (k8s only)
        parameters:
        -   in: path
            name: cloud_account_id
            description: Cloud account id
            required: true
        -   in: body
            name: body
            description: Bulk nodes info
            required: true
            schema:
                type: object
                properties:
                    nodes:
                        type: array
                        items:
                            type: object
                            properties:
                                name: {type: string,
                                    description: "Node name"}
                                flavor: {type: string,
                                    description: "Host flavor"}
                                cpu: {type: integer,
                                    description: "Host CPU"}
                                memory: {type: integer,
                                    description: "Host RAM in GB"}
                                provider_id: {type: string,
                                    description: "Provider id"}
                                last_seen: {type: integer,
                                    description: "Last seen"}
                                hourly_price: {type: number,
                                    description: "Node price per hour"}
        responses:
            200:
                description: Processed objects
                schema:
                    type: object
                    properties:
                        nodes:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description: "Unique node id"}
                                    name: {type: string,
                                        description: "Node name"}
                                    flavor: {type: string,
                                        description: "Host flavor"}
                                    cpu: {type: integer,
                                        description: "Host CPU"}
                                    memory: {type: integer,
                                        description: "Host RAM in GB"}
                                    provider_id: {type: string,
                                        description: "Provider id"}
                                    provider: {type: string,
                                        description: "Provider"}
                                    last_seen: {type: integer,
                                        description: "Last seen"}
                                    deleted_at: {type: integer,
                                        description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer,
                                        description:
                                        "Created timestamp (service field)"}
                                    hourly_price: {type: number,
                                        description: "Node price per hour"}
            400:
                description: |
                    Wrong arguments:
                    - OE0005: Argument doesn't exist
                    - OE0212: Unexpected parameters
                    - OE0216: Argument not provided
                    - OE0214: Argument should be a string/int
                    - OE0215: Wrong argument's length
                    - OE0233: Incorrect body received
                    - OE0385: Argument should be a list
                    - OE0426: Request body should be a dictionary
                    - OE0436: Cloud type is not supported
                    - OE0456: Duplicate path parameters in the request body
                    - OE0475: Invalid request. Parameters provider_id, flavor and hourly_price are all required.
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

        data = self._request_body()
        if not isinstance(data, dict):
            raise OptHTTPError(400, Err.OE0426, [])

        nodes = data.pop('nodes', None)
        if nodes is None:
            raise OptHTTPError(400, Err.OE0216, ['nodes'])
        elif not isinstance(nodes, list):
            raise OptHTTPError(400, Err.OE0385, ['nodes'])

        if data:
            err_args = ','.join(data.keys())
            raise OptHTTPError(400, Err.OE0212, [err_args])

        res = await run_task(self.controller.bulk_create,
                             cloud_account_id, nodes)
        self.set_status(200)
        nodes_dict = {'nodes': [r.to_dict() for r in res]}
        self.write(json.dumps(nodes_dict, cls=ModelEncoder))


class NodesAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                  BaseAuthHandler):
    def _get_controller_class(self):
        return NodesAsyncController

    async def get(self, cloud_account_id):
        """
        ---
        description: |
            List nodes
            Required permission: CLUSTER_SECRET or TOKEN
        tags: [nodes]
        summary: List of cloud account nodes (k8s only)
        parameters:
        -   in: path
            name: cloud_account_id
            description: cloud_account id
            required: true
        responses:
            200:
                schema:
                    type: object
                    properties:
                        nodes:
                            type: array
                            items:
                                type: object
                                properties:
                                    id: {type: string,
                                        description: "Unique node id"}
                                    name: {type: string,
                                        description: "Node name"}
                                    flavor: {type: string,
                                        description: "Host flavor"}
                                    cpu: {type: integer,
                                        description: "Host CPU"}
                                    memory: {type: integer,
                                        description: "Host RAM in GB"}
                                    provider_id: {type: string,
                                        description: "Provider id"}
                                    provider: {type: string,
                                        description: "Provider"}
                                    last_seen: {type: integer,
                                        description: "Last seen"}
                                    deleted_at: {type: integer,
                                        description:
                                        "Deleted timestamp (service field)"}
                                    created_at: {type: integer,
                                        description:
                                        "Created timestamp (service field)"}
                                    hourly_price: {type: number,
                                        description: "Node price per hour"}
            400:
                description: |
                    Unauthorized:
                    - OE0436: Cloud type is not supported
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
        - token: []
        """
        if not self.check_cluster_secret(raises=False):
            cloud_acc = await run_task(
                self.controller.get_cloud_account, cloud_account_id)
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', cloud_acc.organization_id)

        res = await run_task(self.controller.list, cloud_account_id)
        nodes_dict = {'nodes': [r.to_dict() for r in res]}
        self.write(json.dumps(nodes_dict, cls=ModelEncoder))

    def post(self, *args, **kwargs):
        self.raise405()
