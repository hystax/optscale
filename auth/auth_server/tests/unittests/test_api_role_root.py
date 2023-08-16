import uuid
import random
import string
from unittest.mock import patch

from auth.auth_server.models.models import (Type, User, Action, Role, Assignment,
                                            ActionGroup)
from auth.auth_server.models.models import gen_salt
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import hash_password


class TestApiRoleRoot(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version)
        self.partner_scope_id = 'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d'
        self.hierarchy = (
            {'root': {'null': {'partner': {
                'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d':
                    {'customer': {
                        '19a00828-fbff-4318-8291-4b6c14a8066d':
                            {'group': ['be7b4d5e-33b6-40aa-bc6a-00c7d822606f']
                             },
                        '6cfea3e7-a037-4529-9a14-dd9c5151b1f5':
                            {'group': ['e8b8b4e9-a92d-40b5-a5db-b38bf5314ef9',
                                       '42667dde-0427-49be-9541-8e99362ee96e']
                             },
                    }},
                '843f42c4-76b5-467f-b5e3-f7370b1235d6': {'customer': {}}}}}})
        self.admin_user_password = 'toor'
        self.admin_user = self.create_root_user(
            password=self.admin_user_password)
        session = self.db_session
        type_partner = Type(id=10, name='partner',
                            parent=self.admin_user.type)
        self.user_partner_password = 'passwd!!!111'
        salt_p = gen_salt()
        self.user_partner = User('partner@hystax.com', type=type_partner,
                                 password=hash_password(
                                     self.user_partner_password, salt_p),
                                 display_name='Partner user',
                                 scope_id=self.partner_scope_id, salt=salt_p,
                                 type_id=type_partner.id)
        manage_roles_action_group = ActionGroup(name='MANAGE_ROLES')
        manage_users_action_group = ActionGroup(
            name='MANAGE_USERS_ASSIGNMENTS')
        action_create_role = Action(name='CREATE_ROLE', type=type_partner,
                                    action_group=manage_roles_action_group)
        action_list_roles = Action(name='LIST_ROLES', type=type_partner,
                                   action_group=manage_roles_action_group)
        action_list_users = Action(name='LIST_USERS', type=type_partner,
                                   action_group=manage_users_action_group)
        admin_role = Role(name='Super Admin', type=self.admin_user.type,
                          lvl=self.admin_user.type, scope_id=None,
                          description='Super Admin')
        session.add(type_partner)
        session.add(admin_role)
        admin_role.assign_action(action_create_role)
        admin_role.assign_action(action_list_roles)
        admin_role.assign_action(action_list_users)
        assignment_superadmin = Assignment(self.admin_user, admin_role,
                                           self.admin_user.type, None)
        session.add(assignment_superadmin)
        session.commit()
        self.client.token = self.get_token(self.admin_user.email,
                                           self.admin_user_password)

    def test_create_role_root_scope(self):
        code, response = self.client.role_create('Super Admin Role',
                                                 self.admin_user.type.id,
                                                 self.admin_user.type.id, True)
        self.assertEqual(code, 201)
        self.assertTrue(isinstance(response['id'], int))
        self.assertEqual(response['lvl_id'], self.admin_user.type.id)
        self.assertEqual(response['type_id'], self.admin_user.type.id)
        self.assertIsNone(response['scope_id'])

    @patch("auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_list_roles_assignable(self, p_get_hierarchy, p_get_context,
                                   p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_get_context.return_value = {}
        p_res_info.return_value = {}
        code, response = self.client.role_list(
            assignable_to_user_id=self.admin_user.id)
        self.assertEqual(code, 200)
        # will return admin role
        self.assertEqual(len(response), 1)
