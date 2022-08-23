from unittest.mock import patch

from auth_server.models.models import (Type, User, Action, Role, Assignment,
                                       ActionGroup)
from auth_server.models.models import gen_salt
from auth_server.tests.unittests.test_api_base import TestAuthBase
from auth_server.utils import hash_password
import uuid


class TestScopeApi(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version)
        self.partner_scope_id = 'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d'
        self.customer1_scope_id = '19a00828-fbff-4318-8291-4b6c14a8066d'
        self.customer2_scope_id = '6cfea3e7-a037-4529-9a14-dd9c5151b1f5'
        self.group11_scope_id = 'be7b4d5e-33b6-40aa-bc6a-00c7d822606f'
        self.customer3_scope_id = 'c39e4f59-e2a0-4199-80b2-fa688b53598a'
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
                '843f42c4-76b5-467f-b5e3-f7370b1235d6':
                    {'customer': {
                        'c39e4f59-e2a0-4199-80b2-fa688b53598a':
                            {'group': ['4c6a6953-1c31-402d-b864-99790badd361']
                             }
                    }}}}}})
        self.admin_user_password = 'password!'
        self.admin_user = self.create_root_user(
            password=self.admin_user_password)
        session = self.db_session
        self.type_partner = Type(id=10, name='partner',
                                 parent=self.admin_user.type)
        self.type_customer = Type(id=20, name='customer',
                                  parent=self.type_partner)
        self.type_group = Type(id=30, name='group',
                               parent=self.type_customer,
                               assignable=False)
        user_partner_salt = gen_salt()

        self.user_partner_password = 'passwd!!!111'

        self.user_partner = User(
            'partner@domain.com', type=self.type_partner,
            password=hash_password(
                self.user_partner_password, user_partner_salt),
            display_name='Partner user', scope_id=self.partner_scope_id,
            salt=user_partner_salt, type_id=self.type_partner.id)

        self.user_customer = User(
            'user@domain.com', type=self.type_customer,
            password=hash_password(
                self.user_partner_password, user_partner_salt),
            display_name='Customer user', scope_id=self.customer1_scope_id,
            salt=user_partner_salt, type_id=self.type_customer.id)

        user_action_group = ActionGroup(name='MANAGE_USERS')
        role_action_group = ActionGroup(name='MANAGE_ROLES')

        action_list_users = Action(name='CREATE_USER', type=self.type_customer,
                                   action_group=user_action_group)
        action_create_role = Action(name='CREATE_ROLE',
                                    type=self.type_customer,
                                    action_group=role_action_group)
        action_assign_users = Action(name='ASSIGN_USER',
                                     type=self.type_customer,
                                     action_group=user_action_group)

        self.admin_role = Role(name='ADMIN', type=self.type_partner,
                               lvl=self.type_customer,
                               scope_id=self.partner_scope_id,
                               description='Admin',
                               shared=True)

        self.role_lvl_customer = Role(
            name='customer_role', type=self.type_customer,
            lvl=self.type_customer, scope_id=self.customer1_scope_id,
            description='')
        session.add(self.type_partner)
        session.add(self.type_customer)
        session.add(self.type_group)
        session.add(self.user_partner)
        session.add(self.user_customer)

        session.add(self.admin_role)
        session.add(self.role_lvl_customer)

        self.admin_role.assign_action(action_list_users)
        self.admin_role.assign_action(action_assign_users)
        self.admin_role.assign_action(action_create_role)

        assignment_admin = Assignment(self.admin_user, self.admin_role,
                                      self.admin_user.type, None)

        assignment_partner = Assignment(
            self.user_partner, self.admin_role, self.type_partner,
            self.partner_scope_id)

        assignment_customer3 = Assignment(
            self.user_partner, self.admin_role, self.type_customer,
            self.customer3_scope_id
        )

        session.add(assignment_admin)
        session.add(assignment_partner)
        session.add(assignment_customer3)
        session.commit()
        self.client.token = self.get_token(self.user_partner.email,
                                           self.user_partner_password)
        patch('auth_server.controllers.user.UserController.'
              'domain_blacklist').start()

    @patch("auth_server.controllers.base.BaseController.get_context")
    def _create_role(self, p_get_context, name, lvl_id, type_id, context,
                     scope_id=None, is_active=True, shared=False,
                     description=None):
        """
        Wraps create role API
        :param p_get_context:
        :param name:
        :param lvl_id:
        :param type_id:
        :param context:
        :param scope_id:
        :param is_active:
        :param shared:
        :param description:
        :return:
        """
        p_get_context.return_value = context
        return self.client.role_create(name=name, type_id=type_id,
                                       lvl_id=lvl_id, is_active=is_active,
                                       scope_id=scope_id, shared=shared,
                                       description=description)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_scope_user_create(self, p_hierarchy, p_res_info):
        p_hierarchy.return_value = self.hierarchy
        customer1_name = 'Customer1'
        p_res_info.return_value = {
           self.customer1_scope_id: {
                'name': customer1_name,
                'type': 'customer'
            }
        }
        code, scope = self.client.scope_user_create_get()
        self.assertEqual(code, 200)
        self.assertEqual(len(scope), 4)
        self.assertEqual(len(list(filter(lambda x: x['scope_name'] in [
            customer1_name], scope))), 1)
        self.assertEqual(len(list(filter(lambda x: x['scope_type_id'] in [
            self.type_partner.id], scope))), 1)
        self.assertEqual(len(list(filter(lambda x: x['scope_type_id'] in [
            self.type_customer.id], scope))), 3)
        self.assertEqual(len(list(filter(lambda x: x['scope_type_id'] in [
            self.type_group.id], scope))), 0)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_scope_role_create(self, p_hierarchy, p_res_info):
        p_hierarchy.return_value = self.hierarchy
        customer1_name = 'Customer1'
        p_res_info.return_value = {
            self.customer1_scope_id: {
                'name': customer1_name,
                'type': 'customer'
            }
        }
        code, scope = self.client.scope_role_create_get()
        self.assertEqual(code, 200)
        self.assertEqual(len(scope), 4)
        self.assertEqual(len(list(filter(lambda x: x['scope_name'] in [
            customer1_name], scope))), 1)
        self.assertEqual(len(list(filter(lambda x: x['scope_type_id'] in [
            self.type_partner.id], scope))), 1)
        self.assertEqual(len(list(filter(lambda x: x['scope_type_id'] in [
            self.type_customer.id], scope))), 3)
        self.assertEqual(len(list(filter(lambda x: x['scope_type_id'] in [
            self.type_group.id], scope))), 0)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_assign_user_scope_partner_role(self, p_hierarchy, p_res_info):
        """
        Because role have customer lvl, we should see partner
        and corresponding customers
        :param p_hierarchy:
        :param p_res_info:
        :return:
        """
        partner_hierarchy = (
            {'partner': {
                'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d':
                    {'customer': {
                        '19a00828-fbff-4318-8291-4b6c14a8066d':
                            {'group': ['be7b4d5e-33b6-40aa-bc6a-00c7d822606f']
                             },
                        '6cfea3e7-a037-4529-9a14-dd9c5151b1f5':
                            {'group': ['e8b8b4e9-a92d-40b5-a5db-b38bf5314ef9',
                                       '42667dde-0427-49be-9541-8e99362ee96e']
                             },
                    }}}})
        p_hierarchy.side_effect = [partner_hierarchy, self.hierarchy]
        p_res_info.return_value = {}
        code, scope = self.client.scope_user_assign_get(
            self.user_partner.id, self.admin_role.id)
        self.assertEqual(code, 200)
        self.assertEquals(len(scope), 3)
        self.assertEqual(len(list(filter(
            lambda x: x['scope_id'] in [self.partner_scope_id,
                                        self.customer1_scope_id,
                                        self.customer2_scope_id], scope))), 3)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_assign_user_scope_customer_role(self, p_hierarchy, p_res_info):
        hierarchy = ({'customer': {
                        '19a00828-fbff-4318-8291-4b6c14a8066d': {
                            'group': ['be7b4d5e-33b6-40aa-bc6a-00c7d822606f']
                             }}})

        p_hierarchy.side_effect = [hierarchy, self.hierarchy]
        p_res_info.return_value = {}
        code, scope = self.client.scope_user_assign_get(
            self.user_customer.id, self.role_lvl_customer.id)
        self.assertEqual(code, 200)
        self.assertEqual(len(scope), 1)
        self.assertEqual(len(list(filter(
            lambda x: x['scope_id'] in [self.customer1_scope_id], scope))), 1)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_assign_user_scope_bad_request(self, p_hierarchy, p_res_info):
        code, _ = self.client.scope_user_assign_get(
            self.user_customer.id, None)
        self.assertEqual(code, 400)
        code, _ = self.client.scope_user_assign_get(
            None, self.role_lvl_customer.id)
        self.assertEqual(code, 400)
        code, _ = self.client.scope_user_assign_get(
            None, None)
        self.assertEqual(code, 400)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_scope_assign_partner_role(self, p_hierarchy, p_res_info):
        self.client.token = self.get_token(self.admin_user.email,
                                           self.admin_user_password)
        partner_hierarchy = (
            {'partner': {
                'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d':
                    {'customer': {
                        '19a00828-fbff-4318-8291-4b6c14a8066d':
                            {'group': ['be7b4d5e-33b6-40aa-bc6a-00c7d822606f']
                             },
                        '6cfea3e7-a037-4529-9a14-dd9c5151b1f5':
                            {'group': ['e8b8b4e9-a92d-40b5-a5db-b38bf5314ef9',
                                       '42667dde-0427-49be-9541-8e99362ee96e']
                             },
                    }}}})
        p_hierarchy.side_effect = [partner_hierarchy, self.hierarchy]
        p_res_info.return_value = {}
        context = {'partner': self.partner_scope_id}
        _, user = self._create_user(
            email='user@email.com', password='password', display_name='User',
            type_id=self.type_partner.id,
            scope_id=self.partner_scope_id)
        _, role = self._create_role(name='User Role',
                                    lvl_id=self.type_partner.id,
                                    type_id=self.type_partner.id,
                                    context=context,
                                    scope_id=self.partner_scope_id)
        code, scope = self.client.scope_user_assign_get(
            user['id'], role['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(list(filter(lambda x: x['scope_id'] in [
            self.partner_scope_id], scope))), 1)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_scope_assign_customer_role(self, p_hierarchy, p_res_info):
        self.client.token = self.get_token(self.admin_user.email,
                                           self.admin_user_password)
        partner_hierarchy = (
            {'partner': {
                'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d':
                    {'customer': {
                        '19a00828-fbff-4318-8291-4b6c14a8066d':
                            {'group': ['be7b4d5e-33b6-40aa-bc6a-00c7d822606f']
                             },
                        '6cfea3e7-a037-4529-9a14-dd9c5151b1f5':
                            {'group': ['e8b8b4e9-a92d-40b5-a5db-b38bf5314ef9',
                                       '42667dde-0427-49be-9541-8e99362ee96e']
                             },
                    }}}})
        p_hierarchy.side_effect = [partner_hierarchy, self.hierarchy]
        p_res_info.return_value = {}
        context = {'partner': self.partner_scope_id}
        _, user = self._create_user(
            email='user@email.com', password='password', display_name='User',
            type_id=self.type_partner.id,
            scope_id=self.partner_scope_id)
        _, role = self._create_role(name='User Role',
                                    lvl_id=self.type_customer.id,
                                    type_id=self.type_partner.id,
                                    context=context,
                                    scope_id=self.partner_scope_id)
        code, scope = self.client.scope_user_assign_get(
            user['id'], role['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(scope), 3)
        self.assertEqual(len(list(filter(
            lambda x: x['scope_id'] in [self.partner_scope_id,
                                        self.customer1_scope_id,
                                        self.customer2_scope_id], scope))), 3)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_assign_user_scope_invalid_user(self, p_hierarchy, p_res_info):
        hierarchy = ({'customer': {
            '19a00828-fbff-4318-8291-4b6c14a8066d': {
                'group': ['be7b4d5e-33b6-40aa-bc6a-00c7d822606f']
            }}})

        p_hierarchy.side_effect = [hierarchy, self.hierarchy]
        p_res_info.return_value = {}
        for invaild_id in [uuid.uuid4(), 12345, '', '123']:
            code, scope = self.client.scope_user_assign_get(
                invaild_id, self.role_lvl_customer.id)
            self.assertEqual(code, 404)
            self.assertEquals(scope['error']['reason'],
                              'User %s was not found' % invaild_id)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_assign_user_scope_invalid_roles(self, p_hierarchy, p_res_info):
        hierarchy = ({'customer': {
            '19a00828-fbff-4318-8291-4b6c14a8066d': {
                'group': ['be7b4d5e-33b6-40aa-bc6a-00c7d822606f']
            }}})

        p_hierarchy.side_effect = [hierarchy, self.hierarchy]
        p_res_info.return_value = {}
        for invaild_id in [uuid.uuid4(), 12345, '', '123']:
            code, scope = self.client.scope_user_assign_get(
                self.user_customer.id, invaild_id)
            self.assertEqual(code, 404)
            self.assertEquals(scope['error']['reason'],
                              'Role %s was not found' % invaild_id)

    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def _create_user(self, p_hierarchy, email, password, display_name,
                     type_id=None, scope_id=None, is_active=True):
        p_hierarchy.return_value = self.hierarchy
        return self.client.user_create(email, password,
                                       display_name=display_name,
                                       is_active=is_active)
