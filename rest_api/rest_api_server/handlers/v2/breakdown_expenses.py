from rest_api.rest_api_server.controllers.breakdown_expense import BreakdownExpenseAsyncController
from rest_api.rest_api_server.handlers.v2.expenses import BreakdownExpensesBaseAsyncHandler


class BreakdownExpensesAsyncHandler(BreakdownExpensesBaseAsyncHandler):
    def _get_controller_class(self):
        return BreakdownExpenseAsyncController

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get breakdown expenses
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [expenses]
        summary: Get breakdown expenses
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
        -   name: breakdown_by
            in: query
            description: Breakdown by
            required: false
            type: string
            enum: ['employee_id', 'pool_id', 'cloud_account_id',
                'service_name', 'region', 'resource_type', 'k8s_node',
                'k8s_namespace', 'k8s_service']
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
                description: Breakdown expenses data
                schema:
                    type: object
                    properties:
                        total:
                            description: this range expenses sum
                            type: number
                        previous_total:
                            description: previous range expenses sum
                            type: number
                        previous_range_start:
                            description: previous range start
                            type: integer
                        breakdown:
                            type: object
                            description: breakdown by day
                            example:
                                1640995200:
                                    b757aea5-d5a7-45a3-a88d-576ea9590ad2:
                                        cost: 18.80
                                        name: aws
                                        type: aws_cnr
                                    45d15534-d3b6-4505-986a-b0649d056a88:
                                        cost: 3.08
                                        name: azure
                                        type: azure_cnr
                                1641168000:
                                    b757aea5-d5a7-45a3-a88d-576ea9590ad2:
                                        cost: 18.57
                                        name: aws
                                        type: aws_cnr
                                    45d15534-d3b6-4505-986a-b0649d056a88:
                                        cost: 2.15
                                        name: azure
                                        type: azure_cnr
                        counts:
                            type: object
                            description: >
                                total and average expenses by breakdown_by value
                            properties:
                                breakdown_by:
                                    type: object
                                    description: breakdown_by value
                                    properties:
                                        total:
                                            type: number
                                            description: >
                                                this range expenses
                                        previous_total:
                                            type: number
                                            description: >
                                                previous range expenses
                            example: {
                                'abfd6839-22dd-4201-a721-9bc69314cad8': {
                                    'total': 10, 'previous_total': 3}}
                        breakdown_by:
                            type: string
                            description: breakdown_by value
                            example: cloud_account_id
                        start_date:
                            type: integer
                            description: start date (timestamp in seconds)
                            example: 1643673600
                        end_date:
                            type: integer
                            description: end date (timestamp in seconds)
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
                    - OE0515: >
                        The interval between dates should be less than a year
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
