import json

from optscale_exceptions.http_exc import OptHTTPError
from optscale_exceptions.common_exc import WrongArgumentsException
from rest_api_server.controllers.pool_alert import PoolAlertAsyncController
from rest_api_server.exceptions import Err
from rest_api_server.handlers.v1.base_async import (BaseAsyncCollectionHandler,
                                                    BaseAsyncItemHandler)
from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.utils import (
    run_task, ModelEncoder, check_list_attribute, check_int_attribute,
    check_string_attribute, check_dict_attribute, check_bool_attribute)


class ValidateContactsMixin:
    def validate_contacts(self, contacts):
        check_list_attribute('contacts', contacts)
        for contact in contacts:
            check_dict_attribute('contacts', contact)
            employee_id = contact.get('employee_id')
            slack_channel_id = contact.get('slack_channel_id')
            if employee_id is not None and slack_channel_id is None:
                check_string_attribute('employee_id', employee_id)
            elif slack_channel_id is not None and employee_id is None:
                check_string_attribute('slack_channel_id', slack_channel_id)
                slack_team_id = contact.get('slack_team_id')
                check_string_attribute('slack_team_id', slack_team_id)
            else:
                raise WrongArgumentsException(
                    Err.OE0462, ['slack_channel_id,employee_id'])


class PoolAlertsCollectionHandler(BaseAsyncCollectionHandler,
                                  BaseAuthHandler, ValidateContactsMixin):

    def _get_controller_class(self):
        return PoolAlertAsyncController

    async def _validate_params(self, **kwargs):
        try:
            pool_id = kwargs.get('pool_id')
            check_string_attribute('pool_id', pool_id)
            await self.check_permissions('MANAGE_POOLS', 'pool', pool_id)
            contacts = kwargs.get('contacts')
            self.validate_contacts(contacts)
            threshold = kwargs.get('threshold')
            check_int_attribute('threshold', threshold)
            include_children = kwargs.get('include_children')
            if include_children is not None:
                check_bool_attribute('include_children', include_children)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create alert for organization
            Required permission: MANAGE_POOLS for target pool
        tags: [alerts]
        summary: Create alert for organization
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        -   in: body
            name: body
            description: Alert info to add
            required: true
            schema:
                type: object
                properties:
                    pool_id:
                        type: string
                        description: target pool id
                        required: True
                        example: acb35edb-5c37-4dfd-a6b9-06be3135943a
                    include_children:
                        type: boolean
                        description: >
                            Should alert be triggered when child pool
                            exceeded? Default is false
                        required: False
                        example: true
                    threshold:
                        type: integer
                        description: "trigger threshold"
                        required: True
                        example: 80
                    contacts:
                        type: array
                        required: True
                        description: "employees who will be notified"
                        items:
                            type: string
                        example:
                        -   slack_channel_id: D01QNQHESM6
                            slack_team_id: T5CJ5JMH9
                        -   employee_id: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                    based:
                        type: string
                        required: False
                        description: >
                            alert based on ('cost','forecast','constraint',
                            'env_change')"
                        example: 'cost'
                    threshold_type:
                        type: string
                        required: False
                        description: "alert calculation type
                            ('absolute','percentage')"
                        example: 'absolute'
        responses:
            201:
                description: Created (returns created alert)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        threshold_type: absolute
                        based: cost
                        contacts:
                        -   employee_id: 62772eb0-23f9-437b-bfbe-f055f35bbef7
                        -   slack_channel_id: D01QNQHESM6
                            slack_team_id: T5CJ5JMH9
                        last_shoot_at: 0
                        created_at: 1587029026
                        deleted_at: 0
                        include_children: false
            400:
                description: |
                    Wrong arguments:
                    - OE0216: Argument is not provided
                    - OE0214: Argument should be a string
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0233: Incorrect body received
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
                    - OE0385: Argument is not a list
                    - OE0386: Invalid contacts
                    - OE0456: Duplicate path parameters in the request body
            404:
                description: |
                    Not found:
                    - OE0002: Pool not found
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
        security:
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        await self._validate_params(**data)
        res = await run_task(self.controller.create, **data)
        self.set_status(201)
        self.write(res.to_json())

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of alerts for organization
            Required permission: INFO_ORGANIZATION or CLUSTER_SECRET
        tags: [alerts]
        summary: List of alerts for organization
        parameters:
        -   name: organization_id
            in: path
            description: Organization ID
            required: true
            type: string
        responses:
            200:
                description: Alerts list
                schema:
                    type: object
                    example:
                        alerts:
                            type: array
                            items:
                                type: object
                            example:
                                -   id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                                    pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                    threshold_type: absolute
                                    based: forecast
                                    contacts:
                                    -   employee_id: 62772eb0-23f9-437b-bfbe-f055f35bbef7
                                    -   slack_channel_id: D01QNQHESM6
                                        slack_team_id: T5CJ5JMH9
                                    last_shoot_at: 0
                                    created_at: 1587029026
                                    deleted_at: 0
                                    include_children: true
                                -   id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                                    pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                    threshold_type: percentage
                                    based: cost
                                    contacts:
                                    -   employee_id: 62772eb0-23f9-437b-bfbe-f055f35bbef7
                                    last_shoot_at: 0
                                    created_at: 1587029026
                                    deleted_at: 0
                                    include_children: false
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
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                         organization_id)
        res = await run_task(self.controller.list,
                             organization_id=organization_id)
        alerts_dict = {'alerts': [alert.to_dict() for alert in res]}
        self.write(json.dumps(alerts_dict, cls=ModelEncoder))


class PoolAlertsItemHandler(BaseAsyncItemHandler, BaseAuthHandler,
                            ValidateContactsMixin):

    def _get_controller_class(self):
        return PoolAlertAsyncController

    def _validate_params(self, item, **kwargs):
        try:
            threshold = kwargs.get('threshold')
            if threshold is not None:
                check_int_attribute('threshold', threshold)
            contacts = kwargs.get('contacts')
            if contacts is not None:
                self.validate_contacts(contacts)
            include_children = kwargs.get('include_children')
            if include_children is not None:
                check_bool_attribute('include_children', include_children)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        super()._validate_params(item, **kwargs)

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get alert info by ID
            Required permission: MANAGE_POOLS or CLUSTER_SECRET
        tags: [alerts]
        summary: Get alert
        parameters:
        -   name: id
            in: path
            description: Alert ID
            required: true
            type: string
        responses:
            200:
                description: Pool data
                schema:
                    type: object
                    example:
                        id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                        pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        threshold_type: percentage
                        based: cost
                        contacts:
                        -   employee_id: 62772eb0-23f9-437b-bfbe-f055f35bbef7
                        -   slack_channel_id: D01QNQHESM6
                            slack_team_id: T5CJ5JMH9
                        last_shoot_at: 0
                        created_at: 1587029026
                        deleted_at: 0
                        include_children: false
            404:
                description: |
                    Not found:
                    - OE0002: Alert not found
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
        security:
        - token: []
        - secret: []
        """
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('MANAGE_POOLS', 'pool_alert', id)
        await super().get(id, **kwargs)

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Modifies an existing alert
            Required permission: MANAGE_POOLS
        tags: [alerts]
        summary: Edit alert
        parameters:
        -   name: id
            in: path
            description: alert ID
            required: true
            type: string
        -   in: body
            name: body
            description: New alert params
            required: false
            schema:
                type: object
                properties:
                    threshold:
                        type: integer
                        description: "new trigger threshold"
                        required: False
                        example: 80
                    contacts:
                        type: array
                        required: False
                        description: new contacts list
                        items:
                            type: string
                        example:
                        -   slack_channel_id: D01QNQHESM6
                            slack_team_id: T5CJ5JMH9
                    based:
                        type: string
                        required: False
                        description: >
                            alert based on ('cost','forecast', 'constraint',
                            'env_change')
                        example: 'cost'
                    threshold_type:
                        type: string
                        required: False
                        description: "alert calculation type
                            ('absolute','percentage')"
                        example: 'percentage'
                    include_children:
                        type: boolean
                        description: >
                            Should alert be triggered when child pool
                            exceeded? Default is false
                        required: False
                        example: true
        responses:
            201:
                description: Created (returns created alert)
                schema:
                    type: object
                    example:
                        id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                        pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                        threshold_type: absolute
                        based: cost
                        contacts:
                        -   employee_id: 62772eb0-23f9-437b-bfbe-f055f35bbef7
                        -   slack_channel_id: D01QNQHESM6
                            slack_team_id: T5CJ5JMH9
                        last_shoot_at: 0
                        created_at: 1587029026
                        deleted_at: 0
                        include_children: false
            400:
                description: |
                    Wrong arguments:
                    - OE0216: Argument is not provided
                    - OE0214: Argument should be a string
                    - OE0212: Unexpected parameters
                    - OE0215: Wrong argument's length
                    - OE0233: Incorrect body received
                    - OE0223: Argument should be integer
                    - OE0224: Wrong integer argument value
                    - OE0385: Argument is not a list
                    - OE0386: Invalid contacts
            404:
                description: |
                    Not found:
                    - OE0002: Alert not found
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
        security:
        - token: []
        """
        data = self._request_body()
        data.update(kwargs)
        await self.check_permissions('MANAGE_POOLS', 'pool_alert', id)
        await super().patch(id, **data)

    async def delete(self, id, **kwargs):
        """
        ---
        description: |
            Deletes alert with specified id
            Required permission: MANAGE_POOLS
        tags: [alerts]
        summary: Delete alert
        parameters:
        -   name: id
            in: path
            description: Alert ID
            required: true
            type: string
        responses:
            204:
                description: Success
            404:
                description: |
                    Not found:
                    - OE0002: Alert not found
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
        security:
        - token: []
        """
        await self.check_permissions('MANAGE_POOLS', 'pool_alert', id)
        await super().delete(id, **kwargs)


class PoolAlertsProcessHandler(BaseAuthHandler):

    def _get_controller_class(self):
        return PoolAlertAsyncController

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Process alerts for organization
            Required permission: CLUSTER_SECRET
        tags: [alerts]
        summary: Process alerts for organization
        parameters:
        -   name: organization_id
            in: path
            description: Organization id
            required: true
            type: string
        responses:
            200:
                description: Affected alerts
                schema:
                    type: object
                    properties:
                        alerts:
                            type: array
                            items:
                                type: object
                            example:
                                -   id: 86c4fdf2-8920-46dd-b7e0-fff443a43f1c
                                    pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                    threshold_type: absolute
                                    based: forecast
                                    contacts:
                                    -   employee_id: 62772eb0-23f9-437b-bfbe-f055f35bbef7
                                    -   slack_channel_id: D01QNQHESM6
                                        slack_team_id: T5CJ5JMH9
                                    last_shoot_at: 0
                                    created_at: 1587029026
                                    deleted_at: 0
                                    include_children: true
                                -   id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                                    pool_id: 75fc97bc-4f3b-4d25-9715-a8b35273f58d
                                    threshold_type: percentage
                                    based: cost
                                    contacts:
                                    -   employee_id: 62772eb0-23f9-437b-bfbe-f055f35bbef7
                                    last_shoot_at: 0
                                    created_at: 1587029026
                                    deleted_at: 0
                                    include_children: false
            400:
                description: |
                    Wrong arguments:
                    - OE0456: Duplicate path parameters in the request body
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
            403:
                description: |
                    Forbidden:
                    - OE0236: Bad secret
        security:
        - secret: []
        """
        self.check_cluster_secret()
        res = await run_task(self.controller.process_alerts, organization_id)
        result = [alert.to_dict() for alert in res]
        self.set_status(200)
        self.write(json.dumps({'alerts': result}, cls=ModelEncoder))
