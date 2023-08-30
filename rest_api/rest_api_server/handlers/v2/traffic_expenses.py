from rest_api.rest_api_server.controllers.traffic_expense import TrafficExpenseAsyncController
from rest_api.rest_api_server.handlers.v2.expenses import BreakdownExpensesBaseAsyncHandler


class TrafficExpensesAsyncHandler(BreakdownExpensesBaseAsyncHandler):
    def _get_controller_class(self):
        return TrafficExpenseAsyncController

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get traffic expenses
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [traffic_expenses]
        summary: Get traffic expenses
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
                resource_type in format resource_type:identity.
                Supported identity values - [regular, cluster, environment]
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
                description: Traffic expenses data
                schema:
                    type: object
                    properties:
                        traffic_expenses:
                            type: array
                            items:
                                type: object
                            properties:
                                cloud_account_id:
                                    type: string
                                    description: cloud account id
                                cloud_type:
                                    type: string
                                    description: cloud account type
                                from:
                                    type: object
                                    properties:
                                        name:
                                            type: string
                                            description: region name
                                        latitude:
                                            type: number
                                            description: region coordinate
                                        longitude:
                                            type: number
                                            description: region coordinate
                                    description: from region info
                                to:
                                    type: object
                                    properties:
                                        name:
                                            type: string
                                            description: region name
                                        latitude:
                                            type: number
                                            description: region coordinate
                                        longitude:
                                            type: number
                                            description: region coordinate
                                    description: to region info
                                usage:
                                    type: number
                                    description: traffic usage in GB
                                cost:
                                    type: number
                                    description: traffic cost
                            example:
                                -   cloud_account_id:
                                        806908a4-d5c5-44a9-9ead-e45f9fcfaa6c
                                    cloud_type: azure_cnr
                                    from:
                                        name: US Gov Arizona
                                        latitude: 34.42527
                                        longitude: -111.7046
                                    to:
                                        name: usgovarizona
                                        latitude: 34.42527
                                        longitude: -111.7046
                                    usage: 20
                                    cost: 10
                                -   cloud_account_id:
                                        812a5025-abc6-46fa-9857-3a4890bbd62
                                    cloud_type: aws_cnr
                                    from:
                                        name: eu-central-1
                                        latitude: 50.12581
                                        longitude: 8.65399
                                    to:
                                        name: External
                                    usage: 14
                                    cost: 8
                        total_cost:
                            type: number
                            description: total cost
                            example: 16.08
                        total_usage:
                            type: number
                            description: total usage
                            example: 242.424543
                        start_date:
                            type: integer
                            description: start date (timestamp in seconds)
                            example: 1598177929
                        end_date:
                            type: integer
                            description: end date (timestamp in seconds)
                            example: 1600856329
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
        await super().get(organization_id, **url_params)
