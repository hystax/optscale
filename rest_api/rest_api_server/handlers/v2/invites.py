import json

from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  HeraldException)
from etcd import EtcdKeyNotFound

from rest_api.rest_api_server.controllers.invite import InviteAsyncController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler, BaseAsyncItemHandler)
from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.models.enums import InviteAssignmentScopeTypes
from rest_api.rest_api_server.utils import run_task, ModelEncoder, check_dict_attribute


class InviteAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                   BaseAuthHandler):
    def _get_controller_class(self):
        return InviteAsyncController

    def _validate_invites(self, invites, user_info):
        try:
            check_dict_attribute('invites', invites)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        org_ids = []
        pool_ids = []
        for email, invite_assignments in invites.items():
            if email == user_info.get('email'):
                raise OptHTTPError(403, Err.OE0383, [])
            cur_pool_ids = []
            cur_org_ids = []
            for invite_assignment in invite_assignments:
                type_ = invite_assignment.get('scope_type')
                if type_ is None:
                    raise OptHTTPError(400, Err.OE0216, ['scope_type'])
                if type_ == InviteAssignmentScopeTypes.ORGANIZATION.value:
                    cur_org_ids.append(invite_assignment.get('scope_id'))
                elif type_ == InviteAssignmentScopeTypes.POOL.value:
                    cur_pool_ids.append(invite_assignment.get('scope_id'))
                else:
                    raise OptHTTPError(400, Err.OE0436,
                                       [invite_assignment.get('scope_type')])
            if None in cur_pool_ids or None in cur_org_ids:
                raise OptHTTPError(400, Err.OE0216, ['scope_id'])
            for invite_assignment in invite_assignments:
                valid_params = ['scope_id', "scope_type", 'purpose']
                extra_params = list(filter(lambda x: x not in valid_params,
                                           invite_assignment.keys()))
                if extra_params:
                    message = ', '.join(extra_params)
                    raise OptHTTPError(400, Err.OE0212, [message])
            if not cur_pool_ids and not cur_org_ids:
                raise OptHTTPError(400, Err.OE0373, [email])
            if (len(cur_pool_ids) != len(set(cur_pool_ids))) or (
                    len(cur_org_ids) != len(set(cur_org_ids))):
                raise OptHTTPError(400, Err.OE0374, [email])
            org_ids.extend(cur_org_ids)
            pool_ids.extend(cur_pool_ids)
        return org_ids, pool_ids

    async def post(self, **url_params):
        """
        ---
        description: |
            Create invites for users
            Required permission: MANAGE_INVITES
        tags: [invites]
        summary: Create invites for users
        parameters:
        -   in: body
            name: body
            description: invites info to add
            required: true
            schema:
                type: object
                properties:
                    show_link:
                        type: boolean
                        description: show generated invite link (CLUSTER_SECRET required)
                    invites:
                        type: object
                        required: True
                        properties:
                            user1@example.com:
                                type: array
                                items:
                                    type: object
                                    properties:
                                        scope_id:
                                            type: string
                                            description: "Scope id"
                                            required: True
                                            example: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                                        scope_type:
                                            type: string
                                            enum: [organization, pool]
                                            required: true
                                            example: organization
                                        purpose:
                                            type: string
                                            description: "Assigned role purpose
                                                ('add_employee', 'remove_employee',
                                                 'change_role')"
                                            required: False
                                            example: optscale_engineer
        responses:
            201:
                description: Success (returns created objects)
                schema:
                    type: object
                    properties:
                        invites:
                            type: array
                            items:
                                type: object
                            example:
                                -   id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                                    email: user1@example.com
                                    owner_id: 82d18542-1fb1-4094-b48e-7fa96b4ac6c6
                                    owner_name: Mandalorian
                                    organization: Root organization
                                    invite_assignments:
                                        -   scope_id: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                                            scope_type: organization
                                            purpose: optscale_engineer
                                            scope_name: Optscale Engineering
                                            id: 08618433-468e-400d-bc4f-136beb2f9bdc
                                        -   scope_id: 5e2bb869-9f5e-487f-aaf5-ce90e88018d8
                                            scope_type: pool
                                            purpose: optscale_member
                                            scope_name: Optscale Marketing
                                            id: 63ae19a7-c8ff-486d-ac45-c75683e2d611
                                    created_at: 1585680056
                                    deleted_at: 0
                                    ttl: 0
                                -   id: 034a10da-5f90-479b-b06e-10455867747a
                                    email: another@example.com
                                    owner_id: 4bfcdbfd-eef9-4045-afcb-5cae4cc37210
                                    owner_name: Mandalorian
                                    organization: Root organization
                                    invite_assignments:
                                        -   scope_id: 5e2bb869-9f5e-487f-aaf5-ce90e88018d8
                                            scope_type: organization
                                            purpose: optscale_engineer
                                            scope_name: Optscale Marketing
                                    created_at: 1585680056
                                    deleted_at: 0
                                    ttl: 0
            400:
                description: |
                    Wrong arguments:
                    - OE0005: Pool or organization (scope_id) doesn't exist
                    - OE0212: Unexpected parameters
                    - OE0214: Argument should be a string
                    - OE0215: Wrong argument's length
                    - OE0216: Argument not provided
                    - OE0218: Email has invalid format
                    - OE0233: Incorrect body received
                    - OE0287: Bad request: etcd key is missing or value is not a valid RolePurposes
                    - OE0344: Argument is not a dict
                    - OE0373: User is not assigned to any organization
                    - OE0374: Duplicate pool id in assignments
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
                    - OE0383: Invite yourself is forbidden
        security:
        - token: []
        - secret: []
        """
        data = self._request_body()
        invites = data.get('invites', {})
        show_link = data.pop('show_link', False)
        if show_link:
            self.check_cluster_secret()
        user_id = await self.check_self_auth()
        user_info = await self.get_user_info(user_id)

        org_ids, pool_ids = self._validate_invites(invites, user_info)
        try:
            res = await run_task(self.controller.check_user_is_org_manager,
                                 org_ids=org_ids, pool_ids=pool_ids)
            if not res:
                raise OptHTTPError(403, Err.OE0234, [])
        except OptHTTPError as ex:
            if ex.status_code == 404:
                raise OptHTTPError(400, Err.OE0005, ex.params)
            raise

        result = {'invites': []}
        for email, invite_assignments in invites.items():
            try:
                res = await run_task(self.controller.create,
                                     email=email,
                                     user_id=user_id,
                                     user_info=user_info,
                                     invite_assignments=invite_assignments,
                                     show_link=show_link)
            except HeraldException as ex:
                raise OptHTTPError.from_opt_exception(400, ex)
            except EtcdKeyNotFound as ex:
                raise OptHTTPError(400, Err.OE0287, [str(ex)])
            result['invites'].append(res)
        self.set_status(201)
        self.write(json.dumps(result, cls=ModelEncoder))

    async def get(self):
        """
        ---
        description: |
            Get list of invites for current user by token
            Required permission: TOKEN
        tags: [invites]
        summary: List of invites for current user by token
        responses:
            200:
                description: Invites list
                schema:
                    type: object
                    properties:
                        invites:
                            type: array
                            items:
                                type: object
                            example:
                                -   id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                                    email: user1@example.com
                                    owner_id: 82d18542-1fb1-4094-b48e-7fa96b4ac6c6
                                    owner_name: Mandalorian
                                    organization: Root organization
                                    invite_assignments:
                                        -   scope_id: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                                            purpose: optscale_engineer
                                            scope_type: organization
                                            scope_name: Optscale Engineering
                                            id: 08618433-468e-400d-bc4f-136beb2f9bdc
                                        -   scope_id: 5e2bb869-9f5e-487f-aaf5-ce90e88018d8
                                            purpose: optscale_member
                                            scope_type: pool
                                            scope_name: Optscale Marketing
                                            id: 63ae19a7-c8ff-486d-ac45-c75683e2d611
                                    created_at: 1585680056
                                    deleted_at: 0
                                    ttl: 0
                                -   id: 034a10da-5f90-479b-b06e-10455867747a
                                    email: user1@example.com
                                    owner_id: 4bfcdbfd-eef9-4045-afcb-5cae4cc37210
                                    owner_name: Puertoricanian
                                    organization: Another root organization
                                    invite_assignments:
                                        -   scope_id: 82d18542-1fb1-4094-b48e-7fa96b4ac6c6
                                            purpose: optscale_engineer
                                            scope_type: pool
                                            scope_name: Optscale QA
                                    created_at: 1585680056
                                    deleted_at: 0
                                    ttl: 0
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

        user_id = await self.check_self_auth()
        user_info = await self.get_user_info(user_id)
        res = await run_task(self.controller.list, user_id, user_info)
        invites = {'invites': [invite.to_dict() for invite in res]}
        self.write(json.dumps(invites, cls=ModelEncoder))


class InvitesAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return InviteAsyncController

    def _validate_action(self, action):
        if not action:
            raise OptHTTPError(400, Err.OE0216, ['action'])
        if not isinstance(action, str):
            raise OptHTTPError(400, Err.OE0214, ['action'])
        if action not in ['accept', 'decline']:
            raise OptHTTPError(400, Err.OE0166, [action])

    async def patch(self, id, **kwargs):
        """
        ---
        description: |
            Accept or decline invite
            Required permission: TOKEN
        tags: [invites]
        summary: Edit invite
        parameters:
        -   name: id
            in: path
            description: Invite ID
            required: true
            type: string
        -   in: body
            name: body
            description: invite action
            required: true
            schema:
                type: object
                properties:
                    action:
                        type: string
                        example: accept
                        description: "accept or decline invite"
                        required: True
        responses:
            204:
                description: Accepted / declined and deleted
            400:
                description: |
                    Wrong arguments:
                    - OE0216: Action is not provided
                    - OE0214: Action should be a string
                    - OE0166: Action is not supported
                    - OE0233: Incorrect body received
            404:
                description: |
                    Not found:
                    - OE0002: Invite not found
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
        action = data.get('action')
        self._validate_action(action)
        user_id = await self.check_self_auth()
        user_info = await self.get_user_info(user_id)
        action_map = {
            'accept': self.controller.accept_invite,
            'decline': self.controller.decline_invite
        }
        await run_task(action_map[action], id, user_info)
        self.set_status(204)

    async def get(self, id, **kwargs):
        """
        ---
        description: |
            Get invite information
            Required permission: TOKEN
        tags: [invites]
        summary: Get invite info
        parameters:
        -   name: id
            in: path
            description: Invite ID
            required: true
            type: string
        responses:
            200:
                description: Invite info
                schema:
                    type: object
                    example:
                    -   id: 17cb0d9f-2f42-4f26-beeb-220ef946274c
                        email: user1@example.com
                        owner_email: owner@hystax.com,
                        owner_id: 82d18542-1fb1-4094-b48e-7fa96b4ac6c6
                        owner_name: Montezuma
                        organization: Root organization
                        organization_id: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                        invite_assignments:
                            -   scope_id: 44e262cb-d861-45c4-ac85-aaef8edf90f0
                                purpose: optscale_engineer
                                scope_type: organization
                                scope_name: Optscale Engineering
                                id: 08618433-468e-400d-bc4f-136beb2f9bdc
                            -   scope_id: 5e2bb869-9f5e-487f-aaf5-ce90e88018d8
                                purpose: optscale_member
                                scope_type: pool
                                scope_name: Optscale Marketing
                                id: 63ae19a7-c8ff-486d-ac45-c75683e2d611
                        created_at: 1585680056
                        deleted_at: 0
                        ttl: 0
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
                    - OE0002: Invite not found
        security:
        - token: []
        """
        user_id = await self.check_self_auth()
        user_info = await self.get_user_info(user_id)
        res = await run_task(self.controller.get_invite_for_user_info, id,
                             user_info)
        self.write(res.to_json())
