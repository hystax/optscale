import json
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.controllers.rule import RuleAsyncController
from rest_api.rest_api_server.controllers.rule_apply import RuleApplyAsyncController
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.handlers.v2.base import BaseHandler
from rest_api.rest_api_server.utils import (
    run_task, ModelEncoder, check_string_attribute, check_bool_attribute,
    raise_unexpected_exception)
from rest_api.rest_api_server.exceptions import Err


class RuleAsyncCollectionHandler(BaseAsyncCollectionHandler, BaseAuthHandler,
                                 BaseHandler):
    def _get_controller_class(self):
        return RuleAsyncController

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Create pool owner detection rule
            Required permission: INFO_ORGANIZATION
        tags: [rules]
        summary: Create rule
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: body
            description: rule info to add
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: "Name of rule"
                        required: true
                        example: QA instances
                    owner_id:
                        type: string
                        description: "Employee id for resource ownership"
                        required: False
                        example: bd782b9c-3616-4496-99ae-220743eacd55
                    pool_id:
                        type: string
                        description: "Pool id"
                        required: False
                        example: 68e5c9d5-310b-460f-922c-a1d27d6085d7
                    active:
                        type: boolean
                        description: "Rule state"
                        required: False
                        default: true
                        example: true
                    priority:
                        type: integer
                        description: "Rule priority. Defaults to 1"
                        required: False
                        default: 1
                        example: 5
                    conditions:
                        type: array
                        items:
                            type: object
                            properties:
                                type:
                                    type: string,
                                    enum: [name_is, name_starts_with,
                                        name_end_with, name_contains,
                                        resource_type_is, cloud_is,
                                        tag_is, region_is, tag_exists,
                                        tag_value_starts_with]
                                    description: "Condition type"
                                    example: "name_starts_with"
                                meta_info:
                                    type: string,
                                    description: "Value for condition type"
                                    example: "QA_"
        responses:
            201:
                description: Created (returns created object)
                schema:
                    type: object
                    example:
                        owner_id: a201ff8c-691b-4d51-8885-cbccdec05027
                        owner_name: John Doe
                        pool_id: 4f83731b-d3bc-46fd-891e-856a65bbb387
                        pool_purpose: pool
                        pool_name: futureOps.com
                        name: Staging instances
                        organization_id: 08704f0b-9226-452f-8834-47978d4409a6
                        creator_id: a201ff8c-691b-4d51-8885-cbccdec05027
                        creator_name: John Doe
                        conditions:
                        - type: name_starts_with
                          meta_info: QA_
                          id: 02b19579-635d-4d24-a6b5-e753f514c1aa
                        id: a3c6b152-f2ff-4eee-b534-3157f3cb2d9e
                        created_at: '2020-06-26T13:04:58'
                        active: true
                        priority: 1
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument not provided
                    - OE0219: Argument should be valid json
                    - OE0233: Incorrect body received
                    - OE0385: Argument should be a list
                    - OE0344: Argument should be a dict
                    - OE0428: "pool_id" or "owner_id" should be provided
                    - OE0430: Unsupported condition type
                    - OE0456: Duplicate path parameters in the request body
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0378: User is not a member of organization
                    - OE0379: Target owner doesn't have enough permissions for target pool
            404:
                description: |
                    Not found:
                    - OE0002: Organization not found
            409:
                description: |
                    Conflict:
                    - OE0149: Rule with name is already exist
            503:
                description: |
                    Unavailable:
                    - OE0003: Database error. Retry count reached for priority updates
        security:
        - token: []
        """
        await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                     organization_id)
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        user_id = await self.check_self_auth()
        res = await run_task(self.controller.create_rule,
                             user_id, organization_id, self.token, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def get(self, organization_id):
        """
        ---
        description: |
            Get list of rules for organization
            Required permission: INFO_ORGANIZATION
        tags: [rules]
        summary: List of rules
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: query
            name: pool_id
            description: param for filter rules by pool id in target pair
            required: false
            type: string
        -   in: query
            name: owner_id
            description: param for filter rules by owner id in target pair
            required: false
            type: string
        -   in: query
            name: valid_rules_only
            description: parameter for filter invalid rules
            required: false
            type: boolean
            default: false
        responses:
            200:
                description: rule list
                schema:
                    type: object
                    properties:
                        rules:
                            type: array
                            items:
                                type: object
                                example:
                                    id: 78c71cd9-d276-4864-b539-7e86f2d319a5
                                    active: true
                                    creator_id: a201ff8c-691b-4d51-8885-cbccdec05027
                                    creator_name: John Doe
                                    name: QA instances
                                    organization_id: 08704f0b-9226-452f-8834-47978d4409a6
                                    created_at: 1598278245
                                    pool_id: 4f83731b-d3bc-46fd-891e-856a65bbb387
                                    pool_name: futureOps.com
                                    pool_purpose: pool
                                    conditions:
                                    - type: name_starts_with
                                      meta_info: QA_
                                      id: 891c8993-c5ec-4fec-901f-c263cd110e97
                                    owner_id: a201ff8c-691b-4d51-8885-cbccdec05027
                                    owner_name: John Doe
                                    priority: 1
                        entities:
                            type: object
                            example:
                                c3d835c6-3150-4318-a160-d4ad27deba23:
                                    id: c3d835c6-3150-4318-a160-d4ad27deba23
                                    name: my_cloud_name
                                    organization_id: 08704f0b-9226-452f-8834-47978d4409a6
                                    deleted_at: 0
                                    created_at: 1595397424
                                    type: aws_cnr
                                    cloud_account:
                                        access_key_id: myawskeyid
                                        linked: true
                                    auto_import: true
                                    import_period: 1
                                    last_import_at: 1595397424
            400:
                description: |
                    Wrong arguments:
                    - OE0217: Invalid query parameter
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
        """
        await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                     organization_id)
        pool_id = self.get_arg('pool_id', str, None)
        owner_id = self.get_arg('owner_id', str, None)
        valid_rules_only = self.get_arg('valid_rules_only', bool, None)
        res = await run_task(self.controller.get_rules, organization_id,
                             owner_id=owner_id, pool_id=pool_id,
                             valid_rules_only=valid_rules_only)
        self.write(json.dumps(res, cls=ModelEncoder))


class RuleAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return RuleAsyncController

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get rule info by ID
            Required permission: INFO_ORGANIZATION
        tags: [rules]
        summary: Get rule
        parameters:
        -   name: id
            in: path
            description: Rule ID
            required: true
            type: string
        responses:
            200:
                description: Rule data
                schema:
                    type: object
                    example:
                        id: 78c71cd9-d276-4864-b539-7e86f2d319a5
                        active: true
                        creator_id: a201ff8c-691b-4d51-8885-cbccdec05027
                        creator_name: John Doe
                        name: QA instances
                        organization_id: 08704f0b-9226-452f-8834-47978d4409a6
                        created_at: '2020-06-26T12:50:57'
                        pool_id: 4f83731b-d3bc-46fd-891e-856a65bbb387
                        pool_purpose: pool
                        pool_name: futureOps.com
                        conditions:
                        - type: name_starts_with
                          meta_info: QA_
                          id: 891c8993-c5ec-4fec-901f-c263cd110e97
                        owner_id: a201ff8c-691b-4d51-8885-cbccdec05027
                        owner_name: John Doe
                        priority: 1
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
                    - OE0002: Rule not found
        security:
        - token: []
        """
        rule = await self._get_item(id)
        await self.check_permissions(
            'INFO_ORGANIZATION', 'organization', rule.organization_id)
        rule_info = await run_task(self.controller.get_rule_info, rule)
        self.write(json.dumps(rule_info, cls=ModelEncoder))

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Edit existing rule
            Required permission: INFO_ORGANIZATION
        tags: [rules]
        summary: Edit rule
        parameters:
        -   name: id
            in: path
            description: rule ID
            required: true
            type: string
        -   in: body
            name: body
            description: updated rule body
            required: true
            schema:
                type: object
                properties:
                    name:
                        type: string
                        description: "Name of rule"
                        required: False
                        example: QA instances
                    owner_id:
                        type: string
                        description: "Employee id for resource ownership"
                        required: False
                        example: bd782b9c-3616-4496-99ae-220743eacd55
                    active:
                        type: boolean
                        description: "Rule state"
                        required: False
                        example: true
                    pool_id:
                        type: string
                        description: "Pool id"
                        required: False
                        example: 68e5c9d5-310b-460f-922c-a1d27d6085d7
                    priority:
                        type: integer
                        description: "Rule priority"
                        required: False
                        example: 5
                    conditions:
                        type: array
                        required: False
                        items:
                            type: object
                            properties:
                                type:
                                    type: string,
                                    enum: [name_is, name_starts_with,
                                        name_end_with, name_contains,
                                        resource_type_is, cloud_is,
                                        tag_is, region_is, tag_exists,
                                        tag_value_starts_with]
                                    description: "Condition type"
                                    example: "name_starts_with"
                                meta_info:
                                    type: string,
                                    description: "Value for condition type"
                                    example: "QA_"
        responses:
            200:
                description: Rule data
                schema:
                    type: object
                    example:
                        id: 78c71cd9-d276-4864-b539-7e86f2d319a5
                        active: true
                        creator_id: a201ff8c-691b-4d51-8885-cbccdec05027
                        creator_name: John Doe
                        name: QA instances
                        organization_id: 08704f0b-9226-452f-8834-47978d4409a6
                        created_at: '2020-06-26T12:50:57'
                        pool_id: 4f83731b-d3bc-46fd-891e-856a65bbb387
                        pool_purpose: pool
                        pool_name: futureOps.com
                        conditions:
                        - type: name_starts_with
                          meta_info: QA_
                          id: 891c8993-c5ec-4fec-901f-c263cd110e97
                        owner_id: a201ff8c-691b-4d51-8885-cbccdec05027
                        owner_name: John Doe
                        priority: 1
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument not provided
                    - OE0219: Argument should be valid json
                    - OE0233: Incorrect body received
                    - OE0385: Argument should be a list
                    - OE0344: Argument should be a dict
                    - OE0428: "pool_id" or "owner_id" should be provided
                    - OE0430: Unsupported condition type
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0378: User is not a member of organization
                    - OE0379: Target owner doesn't have enough permissions for target pool
            404:
                description: |
                    Not found:
                    - OE0002: Rule not found
            409:
                description: |
                    Conflict:
                    - OE0149: Rule with name is already exist
            503:
                description: |
                    Unavailable:
                    - OE0003: Database error. Retry count reached for priority updates
        security:
        - token: []
        """
        data = self._request_body()
        item = await self._get_item(id)
        await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                     item.organization_id)
        self._validate_params(item, **kwargs)
        res = await run_task(self.controller.edit_rule, id, self.token, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    async def delete(self, id, **kwargs):
        """
        ---
        description: |
            Deletes rule with specified id
            Required permission: INFO_ORGANIZATION
        tags: [rules]
        summary: Delete rule
        parameters:
        -   name: id
            in: path
            description: Rule ID
            required: true
            type: string
        responses:
            204:
                description: Success
            401:
                description: |
                    Unauthorized:
                    - OE0237: This resource requires authorization
            404:
                description: |
                    Not found:
                    - OE0002: Rule not found
            503:
                description: |
                    Unavailable:
                    - OE0003: Database error. Retry count reached for priority updates
        security:
        - token: []
        """
        item = await self._get_item(id)
        await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                     item.organization_id)
        await super().delete(id, **kwargs)


class RulePriorityAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return RuleAsyncController

    def get(self, id, **kwargs):
        self.raise405()

    def delete(self, id, **kwargs):
        self.raise405()

    async def patch(self, rule_id, **kwargs):
        """
        ---
        description: |
            Prioritize the rule
            Required permission: INFO_ORGANIZATION
        tags: [rules]
        summary: Prioritize the rule
        parameters:
        -   in: path
            name: rule_id
            description: rule id
            required: true
        -   in: body
            name: body
            description: body with action
            required: true
            schema:
                type: object
                properties:
                    action:
                        type: string
                        description: Prioritization action
                        enum: [prioritize,promote,demote,deprioritize]
                        required: True
                        example: prioritize
        responses:
            200:
                description: organization rules
                schema:
                    type: object
                    properties:
                        rules:
                            type: array
                            items:
                                type: object
                                example:
                                    id: 78c71cd9-d276-4864-b539-7e86f2d319a5
                                    active: true
                                    creator_id: a201ff8c-691b-4d51-8885-cbccdec05027
                                    creator_name: John Doe
                                    name: QA instances
                                    organization_id: 08704f0b-9226-452f-8834-47978d4409a6
                                    created_at: 1598278245
                                    pool_id: 4f83731b-d3bc-46fd-891e-856a65bbb387
                                    pool_name: futureOps.com
                                    pool_purpose: pool
                                    conditions:
                                    - type: name_starts_with
                                      meta_info: QA_
                                      id: 891c8993-c5ec-4fec-901f-c263cd110e97
                                    owner_id: a201ff8c-691b-4d51-8885-cbccdec05027
                                    owner_name: John Doe
                                    priority: 1
                        entities:
                            type: object
                            example:
                                c3d835c6-3150-4318-a160-d4ad27deba23:
                                    id: c3d835c6-3150-4318-a160-d4ad27deba23
                                    name: my_cloud_name
                                    organization_id: 08704f0b-9226-452f-8834-47978d4409a6
                                    deleted_at: 0
                                    created_at: 1595397424
                                    type: aws_cnr
                                    cloud_account:
                                        access_key_id: myawskeyid
                                        linked: true
                                    auto_import: true
                                    import_period: 1
                                    last_import_at: 1595397424
            400:
                description: |
                    Wrong arguments:
                    - OE0216: Argument is not provided
                    - OE0166: Action is not supported
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
            503:
                description: |
                    Unavailable:
                    - OE0003: Database error. Retry count reached for priority updates
        security:
        - token: []
        """
        item = await self._get_item(rule_id)
        await self.check_permissions('INFO_ORGANIZATION', 'organization',
                                     item.organization_id)
        data = self._request_body()
        res = await run_task(self.controller.update_priority, rule_id, **data)
        self.write(json.dumps(res, cls=ModelEncoder))


class RulesApplyAsyncHandler(BaseAsyncItemHandler, BaseAuthHandler,
                             BaseHandler):
    def _get_controller_class(self):
        return RuleApplyAsyncController

    async def _validate_params(self, **kwargs):
        pool_id = kwargs.pop('pool_id', None)
        check_string_attribute('pool_id', pool_id)
        include_children = kwargs.pop('include_children', None)
        if include_children is not None:
            check_bool_attribute('include_children', include_children)
        if kwargs:
            raise_unexpected_exception(kwargs)

    async def post(self, organization_id, **url_params):
        """
        ---
        description: |
            Re-apply assignment rules to resources in specified pools
            Required permission: MANAGE_POOLS
        tags: [rules]
        summary: Re-apply assignment rules
        parameters:
        -   in: path
            name: organization_id
            description: organization id
            required: true
        -   in: body
            name: body
            description: apply parameters
            required: true
            schema:
                type: object
                properties:
                    pool_id:
                        type: string
                        description: >
                            Target pool id
                        required: True
                        example: 68e5c9d5-310b-460f-922c-a1d27d6085d7
                    include_children:
                        type: boolean
                        description: >
                            Set to true if rules also should be applied to all
                            child pools of the specified pool
                        required: False
                        default: false
                        example: true
        responses:
            201:
                description: Assigment rules re-applied
                schema:
                    type: object
                    example:
                        processed: 10
                        updated_assignments: 4
            400:
                description: |
                    Wrong arguments:
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0226: Wrong boolean value
                    - OE0233: Incorrect body received
                    - OE0416: Argument should not contain only whitespaces
                    - OE0456: Duplicate path parameters in the request body
            401:
                description: |
                    Unauthorized:
                    - OE0235: Unauthorized
                    - OE0237: This resource requires authorization
            403:
                description: |
                    Forbidden:
                    - OE0234: Forbidden
                    - OE0378: Current user is not a member in organization
            404:
                description: |
                    Not found:
                    - OE0002: Organization or pool not found
        security:
        - token: []
        """
        data = self._request_body()
        data.update(url_params)
        try:
            await self._validate_params(**data)
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)
        pool_id = data.get('pool_id')
        await self.check_permissions('MANAGE_POOLS', 'pool', pool_id)
        user_id = await self.check_self_auth()
        user_info = await self.get_user_info(user_id)
        res = await run_task(self.controller.reapply_rules, user_info,
                             organization_id, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))
