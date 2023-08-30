from rest_api.rest_api_server.controllers.available_filters import AvailableFiltersAsyncController
from rest_api.rest_api_server.handlers.v2.expenses import FilteredExpensesBaseAsyncHandler


class AvailableFiltersAsyncHandler(FilteredExpensesBaseAsyncHandler):

    def _get_controller_class(self):
        return AvailableFiltersAsyncController

    async def get(self, organization_id, **url_params):
        """
        ---
        description: |
            Get available filters
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [expenses]
        summary: Get available filters for expenses
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
                description: Available filters data
                schema:
                    type: object
                    properties:
                        filter_values:
                            type: object
                            description: >
                                values which can be used for filters in current
                                date range excluding current filters
                            properties:
                                cloud_account:
                                    type: array
                                    description: >
                                        list of cloud accounts which can be used
                                        for filtering in the same date range
                                    items:
                                        type: object
                                        properties:
                                            id:
                                                type: string
                                                description: cloud account id
                                                example: 2329c0fb-8e09-432c-b985-f52d1ebe5e61
                                            name:
                                                type: string
                                                description: cloud account name
                                                example: aws
                                            type:
                                                type: string
                                                description: cloud type
                                                example: aws_cnr
                                pool:
                                    type: array
                                    description: >
                                        list of pools which can be used
                                        for filtering in the same date range
                                    items:
                                        type: object
                                        properties:
                                            id:
                                                type: string
                                                description: pool id
                                                example: e242f0d8-1e4a-40de-b1e5-8a334834d6c4
                                            name:
                                                type: string
                                                description: pool name
                                                example: aws
                                            purpose:
                                                type: string
                                                description: pool purpose
                                                example: pool
                                owner:
                                    type: array
                                    description: >
                                        list of owners which can be used
                                        for filtering in the same date range
                                    items:
                                        type: object
                                        properties:
                                            id:
                                                type: string
                                                description: owner id
                                                example: aa6bae93-4abd-4f54-8e3b-a2c72e6b7a6d
                                            name:
                                                type: string
                                                description: owner name
                                                example: aws
                                resource_type:
                                    type: array
                                    description: >
                                        list of resource types which can be used
                                        for filtering in the same date range
                                    items:
                                        type: object
                                        properties:
                                            name:
                                                type: string
                                                description: resource type name
                                                example: Snapshot
                                            type:
                                                type: string
                                                description: resource type environment
                                                example: None
                                service_name:
                                    type: array
                                    description: >
                                        list of service names which can be used
                                        for filtering in the same date range
                                    items:
                                        type: object
                                        properties:
                                            name:
                                                type: string
                                                description: service name
                                                example: Amazon EC2
                                            cloud_type:
                                                type: string
                                                description: cloud type
                                                example: aws_cnr
                                region:
                                    type: array
                                    description: >
                                        list of regions which can be used
                                        for filtering in the same date range
                                    items:
                                        type: object
                                        properties:
                                            name:
                                                type: string
                                                description: region name
                                                example: us-east-1
                                            cloud_type:
                                                type: string
                                                description: cloud type
                                                example: aws_cnr
                                tag:
                                    type: array
                                    description: >
                                        list of tag keys which can be used
                                        for filtering in the same date range
                                    items:
                                        type: string
                                        description: tag key
                                    example:
                                    - hello
                                    - world
                                without_tag:
                                    type: array
                                    description: >
                                        list of tag keys that are discarded
                                        for filtering in the same date range
                                    items:
                                        type: string
                                        description: tag key
                                    example:
                                    - hello
                                    - world
                                k8s_node:
                                    type: array
                                    description: >
                                        list of k8s nodes which can be used
                                        for filtering in the same date range
                                    items:
                                        type: object
                                        properties:
                                            name:
                                                type: string
                                                description: k8s node name
                                                example: ubuntu
                                            cloud_type:
                                                type: string
                                                description: >
                                                    cloud type (can be used only for kubernetes cloud)
                                                example: kubernetes_cnr
                                k8s_namespace:
                                    type: array
                                    description: >
                                        list of k8s namespaces which can be used
                                        for filtering in the same date range
                                    items:
                                        type: object
                                        properties:
                                            name:
                                                type: string
                                                description: k8s namespace
                                                example: kube-system
                                            cloud_type:
                                                type: string
                                                description: >
                                                    cloud type (can be used only for kubernetes cloud)
                                                example: kubernetes_cnr
                                k8s_service:
                                    type: array
                                    description: >
                                        list of k8s services which can be used
                                        for filtering in the same date range
                                    items:
                                        type: object
                                        properties:
                                            name:
                                                type: string
                                                description: k8s service
                                                example: kube-dns
                                            cloud_type:
                                                type: string
                                                description: >
                                                    cloud type (can be used only for kubernetes cloud)
                                                example: kubernetes_cnr
                                active:
                                    type: array
                                    description: >
                                        list of values which can be passed to
                                        active filter to filter current dataset
                                    items:
                                        type: boolean
                                        description: active filter value
                                    example:
                                    - true
                                    - false
                                recommendations:
                                    type: array
                                    description: >
                                        list of values which can be passed to
                                        recommendations filter to filter current
                                        dataset
                                    items:
                                        type: boolean
                                        description: recommendations filter value
                                    example:
                                    - true
                                    - false
                                constraint_violated:
                                    type: array
                                    description: >
                                        list of values which can be passed to
                                        constraint_violated filter to filter
                                        current dataset
                                    items:
                                        type: boolean
                                        description: constraint_violated filter value
                                    example:
                                    - true
                                    - false
                                traffic_from:
                                    type: array
                                    description: >
                                        list of values which can be passed to
                                        traffic_from filter to filter
                                        current dataset
                                    items:
                                        type: object
                                        properties:
                                            name:
                                                type: string
                                                description: region name
                                                example: eu-south-1
                                            cloud_type:
                                                type: string
                                                description: cloud type
                                                example: aws_cnr
                                traffic_to:
                                    type: array
                                    description: >
                                        list of values which can be passed to
                                        traffic_to filter to filter
                                        current dataset
                                    items:
                                        type: object
                                        properties:
                                            name:
                                                type: string
                                                description: region name
                                                example: eu-south-1
                                            cloud_type:
                                                type: string
                                                description: cloud type
                                                example: aws_cnr
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
