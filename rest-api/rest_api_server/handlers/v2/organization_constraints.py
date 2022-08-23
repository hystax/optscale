import json

from rest_api_server.controllers.organization_constraint import (
    OrganizationConstraintAsyncController)
from rest_api_server.handlers.v1.base_async import (BaseAsyncCollectionHandler,
                                                    BaseAsyncItemHandler)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.handlers.v2.base import BaseHandler
from rest_api_server.utils import run_task, ModelEncoder


class OrganizationConstraintsAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                                    BaseAuthHandler, BaseHandler):

    def _get_controller_class(self):
        return OrganizationConstraintAsyncController

    async def post(self, organization_id, **params):
        """
        ---
        description: |
            Create constraint for organization
            Required permission: EDIT_PARTNER
        tags: [organization_constraints]
        summary: Create constraint for organization
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Organization constraint info to add
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: organization constraint name
                        required: True
                        example: no instances in eu-central-1
                    type:
                        type: string
                        required: True
                        description: Organization constraint type
                        enum: [expense_anomaly, resource_count_anomaly,
                               resource_quota, recurring_budget,
                               expiring_budget, tagging_policy]
                        example: 'resource_count_anomaly'
                    definition:
                        type: object
                        required: True
                        properties:
                            threshold:
                                type: integer
                                description: >
                                    threshold value (for expense_anomaly and
                                    resource_count_anomaly types)
                                required: True
                                example: 30
                            threshold_days:
                                type: integer
                                description: >
                                    number of days for average calculating (for
                                    expense_anomaly and resource_count_anomaly
                                    types)
                                    cannot exceed 180
                                required: True
                                example: 7
                            max_value:
                                type: integer
                                description: >
                                    resources count limit for day (for
                                    resource_quota type)
                                required: True
                                example: 7
                            total_budget:
                                type: integer
                                description: >
                                    expense limit (for expiring_budget type)
                                required: True
                                example: 7
                            start_date:
                                type: integer
                                description: >
                                    expenses start date timestamp (for
                                    expiring_budget and tagging_policy types)
                                required: True
                                example: 1647422121
                            monthly_budget:
                                type: integer
                                description: >
                                    expense limit for month (for
                                    recurring_budget type)
                                required: True
                                example: 7
                            conditions:
                                type: object
                                description: set of AND-ed rules
                                required: True
                                properties:
                                    tag:
                                        type: string
                                        required: False
                                        example: tag1
                                    without_tag:
                                        type: string
                                        required: False
                                        example: tag2
                    filters:
                        description: set of filters for dataset
                        type: object
                        required: True
                        properties:
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
                                description: pool id
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
                            -   name: traffic_from
                                in: query
                                description: <region_name>:<cloud_type>
                                required: false
                                type: array
                                collectionFormat: multi
                                items:
                                    type: string
                            -   name: traffic_to
                                in: query
                                description: <region_name>:<cloud_type>
                                required: false
                                type: array
                                collectionFormat: multi
                                items:
                                    type: string
                        example:
                            pool_id:
                                - 4482ed2a-50b9-448a-8c46-2727f352a7e3
                            region:
                                - eu-north-1
        responses:
            201:
                description: Created (returns created constraint)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        name: no instances in eu-central-1
                        organization_id: db39e3ac-94a7-44cd-b7dc-4be5d3213aa8
                        type: resource_count_anomaly
                        definition:
                            threshold_days: 7
                            threshold: 30
                        filters:
                            pool:
                              - id: 4482ed2a-50b9-448a-8c46-2727f352a7e3
                                name: Pool1
                                purpose: business_unit
                            region:
                              - name: eu-north-1
                                cloud_type: aws_cnr
                        created_at: 1587029026
                        deleted_at: 0
                        last_run: 0
                        last_run_result: {}
            400:
                description: |
                    Wrong arguments:
                    - OE0004: type is not a valid OrganizationConstraintTypes
                    - OE0211: Parameter is immutable
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument not provided
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
                    - OE0233: Incorrect body received
                    - OE0344: Argument should be a dictionary
                    - OE0385: Argument should be a list
                    - OE0456: Duplicate path parameters in the request body
                    - OE0496: Argument should not consist of only wildcards
                    - OE0499: Incorrect resource type identity
                    - OE0504: Filtering is unavailable
                    - OE0517: tag or without_tag should be provided
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Organization/Pool/Employee/CloudAccount not found
        security:
        - token: []
        """
        await self.check_permissions(
                'EDIT_PARTNER', 'organization', organization_id)
        await super().post(organization_id=organization_id, **params)

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of constraints for organization
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [organization_constraints]
        summary: List of constraints for organization
        parameters:
        -   in: path
            name: organization_id
            description: id of the organization
            required: true
        -   in: query
            name: hit_days
            description: |
                number of days to get organization constraint limit hits for
            required: false
        -   in: query
            name: type
            description: Organization constraint types
            enum: [expense_anomaly, resource_count_anomaly,
               resource_quota, recurring_budget,
               expiring_budget, tagging_policy]
            required: false
        responses:
            200:
                description: organization constraints list
                schema:
                    type: object
                    properties:
                        organization_constraints:
                            type: array
                            items:
                                type: object
                                example:
                                    id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                                    name: my_expense_anomaly
                                    organization_id: db39e3ac-94a7-44cd-b7dc-4be5d3213aa8
                                    type: expense_anomaly
                                    definition:
                                        threshold_days: 7
                                        threshold: 30
                                    filters:
                                        pool:
                                          - id: 4482ed2a-50b9-448a-8c46-2727f352a7e3
                                            name: Pool1
                                            purpose: business_unit
                                        region:
                                          - name: eu-north-1
                                            cloud_type: aws_cnr
                                    created_at: 1587029026
                                    deleted_at: 0
                                    last_run: 1644309325
                                    limit_hits:
                                        -   deleted_at: 0
                                            id: e4650176-6b34-4dce-b503-193388003be8
                                            created_at: 1644309325
                                            constraint_limit: 31
                                            value: 79
                                            organization_id: db39e3ac-94a7-44cd-b7dc-4be5d3213aa8
                                            constraint_id: e3228e58-3bb2-42d4-8aec-c0ce552196b5
                                    last_run_result:
                                        average: 29
                                        today: 79
                                        breakdown:
                                            1643709325: 28
                                            1643809325: 28
                                            1643909325: 28
                                            1644009325: 30
                                            1644109325: 30
                                            1644209325: 30
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: Organization/Pool/Employee/CloudAccount not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization', organization_id)
        hit_days = self.get_arg('hit_days', int)
        type = self.get_arg('type', str, repeated=True)
        res = await run_task(self.controller.list,
                             organization_id=organization_id,
                             hit_days=hit_days, type=type)
        constraints = {'organization_constraints': [
            constraint.to_dict() for constraint in res
        ]}
        self.write(json.dumps(constraints, cls=ModelEncoder))


class OrganizationConstraintsAsyncItemHandler(BaseAsyncItemHandler,
                                              BaseAuthHandler):

    def _get_controller_class(self):
        return OrganizationConstraintAsyncController

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get organization constraint info by ID
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [organization_constraints]
        summary: Get organization constraint
        parameters:
        -   name: id
            in: path
            description: Organization constraint ID
            required: true
            type: string
        responses:
            200:
                description: Organization constraint data
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        name: my_expense_anomaly
                        organization_id: 4482ed2a-50b9-448a-8c46-2727f352a7e3
                        type: expense_anomaly
                        definition:
                            threshold_days: 7
                            threshold: 30
                        filters:
                            pool:
                                - id: 4482ed2a-50b9-448a-8c46-2727f352a7e3
                                  name: Pool1
                                  purpose: business_unit
                            region:
                                - name: eu-north-1
                                  cloud_type: aws_cnr
                        created_at: 1587029026
                        deleted_at: 0
                        last_run: 1644309325
                        last_run_result:
                            average: 29
                            today: 79
                            breakdown:
                                1643709325: 28
                                1643809325: 28
                                1643909325: 28
                                1644009325: 30
                                1644109325: 30
                                1644209325: 30
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            404:
                description: |
                    Not found:
                    - OE0002: OrganizationConstraint/Organization/Pool/Employee/CloudAccount not found
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                'INFO_ORGANIZATION', 'organization_constraint', id)
        res = await run_task(self.controller.get_constraint, item_id=id)
        self.write(res.to_json())

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing constraint
            Required permission: EDIT_PARTNER or CLUSTER_SECRET
        tags: [organization_constraints]
        summary: Edit organization constraint
        parameters:
        -   name: id
            in: path
            description: Organization constraint ID
            required: True
            type: string
        -   in: body
            name: body
            description: New constraint params
            required: True
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: organization constraint name
                        required: False
                        example: no instances in eu-central-1
                    last_run:
                        type: integer
                        description: last constraint check timestamp
                        required: False
                        example: 0
                    last_run_result:
                        type: object
                        description: last run result (constraint type specific)
                        required: False
                        example:
                            average: 29
                            today: 79
                            breakdown:
                                1643709325: 28
                                1643809325: 28
                                1643909325: 28
                                1644009325: 30
                                1644109325: 30
                                1644209325: 30
        responses:
            200:
                description: Success (returns modified constraint)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        name: my_expense_anomaly
                        organization_id: 4482ed2a-50b9-448a-8c46-2727f352a7e3
                        type: expense_anomaly
                        definition:
                            threshold_days: 7
                            threshold: 30
                        filters:
                            pool:
                              - id: 4482ed2a-50b9-448a-8c46-2727f352a7e3
                                name: Pool1
                                purpose: budget
                            region:
                              - name: eu-north-1
                                cloud_type: aws_cnr
                        created_at: 1587029026
                        deleted_at: 0
                        last_run: 1644309325
                        last_run_result:
                            average: 29
                            today: 79
                            breakdown:
                                1643709325: 28
                                1643809325: 28
                                1643909325: 28
                                1644009325: 30
                                1644109325: 30
                                1644209325: 30
            400:
                description: |
                    Wrong arguments:
                    - OE0211: Parameter is immutable
                    - OE0216: Argument not provided
                    - OE0214: Argument should be a string
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0233: Incorrect body received
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
            404:
                description: |
                    Not found:
                    - OE0002: OrganizationConstraint/Organization/Pool/Employee/CloudAccount not found
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
        security:
        - token: []
        - secret: []
        """
        data = self._request_body()
        data.update(kwargs)
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions(
                    'EDIT_PARTNER', 'organization_constraint', id)
        await super().patch(id, **data)

    async def delete(self, id, **kwargs):
        """
        ---
        description: |
            Deletes organization constraint with specified id
            Required permission: EDIT_PARTNER
        tags: [organization_constraints]
        summary: Delete organization constraint
        parameters:
        -   name: id
            in: path
            description: Organization constraint ID
            required: true
            type: string
        responses:
            204:
                description: Success
            404:
                description: |
                    Not found:
                    - OE0002: OrganizationConstraint not found
            403:
                description: |
                    Forbidden:
                    - OE0003: Forbidden
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
        security:
        - token: []
        """
        await self.check_permissions(
            'EDIT_PARTNER', 'organization_constraint', id)
        await run_task(self.controller.get_constraint, id)
        await run_task(self.controller.delete_constraint_by_id, id)
        self.set_status(204)
