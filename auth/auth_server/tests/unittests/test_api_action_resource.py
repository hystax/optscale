from unittest.mock import patch

from auth_server.models.models import (Type, User, Action, Role, Assignment,
                                       ActionGroup)
from auth_server.models.models import gen_salt
from auth_server.tests.unittests.test_api_base import TestAuthBase
from auth_server.utils import hash_password


class TestActionResourcesApi(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version=version)
        self.partner_scope_id = 'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d'
        self.customer1_scope_id = '19a00828-fbff-4318-8291-4b6c14a8066d'
        self.customer2_scope_id = '6cfea3e7-a037-4529-9a14-dd9c5151b1f5'
        self.partner2_scope_id = '843f42c4-76b5-467f-b5e3-f7370b1235d6'
        self.customer3_scope_id = 'c39e4f59-e2a0-4199-80b2-fa688b53598a'
        self.group3_scope_id = '4c6a6953-1c31-402d-b864-99790badd361'
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
            'partner@example.com', type=self.type_partner,
            password=hash_password(
                self.user_partner_password, user_partner_salt),
            display_name='Partner user', scope_id=self.partner_scope_id,
            salt=user_partner_salt, type_id=self.type_partner.id)
        self.user_customer = User(
            'user@example.com', type=self.type_customer,
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
        self.admin_role.assign_action(action_create_role)

        assignment_admin = Assignment(self.admin_user, self.admin_role,
                                      self.admin_user.type, None)

        assignment_partner = Assignment(
            self.user_partner, self.admin_role, self.type_partner,
            self.partner_scope_id)

        assignment_customer3 = Assignment(
            self.user_customer, self.admin_role, self.type_customer,
            self.customer3_scope_id
        )

        session.add(assignment_admin)
        session.add(assignment_partner)
        session.add(assignment_customer3)
        session.commit()

    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_action_partner_resources(self, p_hierarchy):
        p_hierarchy.return_value = self.hierarchy
        self.client.token = self.get_token(self.user_partner.email,
                                           self.user_partner_password)
        code, response = self.client.action_resources_get(['CREATE_USER'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['CREATE_USER']), 3)
        self.assertEqual(len(list(filter(lambda x: x[1] in [
            self.partner_scope_id, self.customer1_scope_id,
            self.customer2_scope_id], response['CREATE_USER']))), 3)

    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_action_customer_resources1(self, p_hierarchy):
        p_hierarchy.return_value = self.hierarchy
        self.client.token = self.get_token(self.user_customer.email,
                                           self.user_partner_password)
        code, response = self.client.action_resources_get(
            ['CREATE_USER', 'CREATE_ROLE'])
        self.assertEqual(code, 200)
        self.assertEqual(len(list(filter(lambda x: x[1] in [
            self.customer3_scope_id], response['CREATE_USER']))), 1)
        self.assertEqual(len(list(filter(lambda x: x[1] in [
            self.customer3_scope_id], response['CREATE_ROLE']))), 1)

    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_action_customer_non_assignable(self, p_hierarchy):
        p_hierarchy.return_value = self.hierarchy
        self.client.token = self.get_token(self.user_customer.email,
                                           self.user_partner_password)
        code, response = self.client.action_resources_get(
            ['CREATE_USER'], assignable_only=False)
        self.assertEqual(code, 200)
        self.assertEqual(len(list(filter(lambda x: x[1] in [
            self.customer3_scope_id, self.group3_scope_id],
                                         response['CREATE_USER']))), 2)

    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_action_root(self, p_hierarchy):
        p_hierarchy.return_value = self.hierarchy
        self.client.token = self.get_token(self.admin_user.email,
                                           self.admin_user_password)
        code, response = self.client.action_resources_get(
            ['CREATE_USER'])
        self.assertEqual(code, 200)
        self.assertEqual(len(list(filter(lambda x: x[1] in [
            self.partner_scope_id, self.partner2_scope_id,
            self.customer1_scope_id, self.customer2_scope_id,
            self.customer3_scope_id], response['CREATE_USER']))), 5)

    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_action_user_id(self, p_hierarchy):
        p_hierarchy.return_value = self.hierarchy
        code, response = self.client.action_resources_get(
            ['CREATE_USER'], user_id=self.admin_user.id)
        self.assertEqual(code, 200)
        self.assertEqual(len(list(filter(lambda x: x[1] in [
            self.partner_scope_id, self.partner2_scope_id,
            self.customer1_scope_id, self.customer2_scope_id,
            self.customer3_scope_id], response['CREATE_USER']))), 5)

    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_bulk_action_resources(self, p_hierarchy):
        p_hierarchy.return_value = self.hierarchy
        user_ids = [self.admin_user.id, self.user_partner.id,
                    self.user_customer.id]
        code, response = self.client.bulk_action_resources_get(
            user_ids, ['CREATE_USER'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response), len(user_ids))
        self.assertCountEqual(response.keys(), user_ids)
        for user_id in user_ids:
            self.assertCountEqual(response[user_id].keys(),
                                  ['CREATE_USER'])
        admin_response = response[self.admin_user.id]
        self.assertCountEqual(admin_response['CREATE_USER'], [
            ['root', None],
            ['partner', self.partner_scope_id],
            ['partner', self.partner2_scope_id],
            ['customer', self.customer1_scope_id],
            ['customer', self.customer2_scope_id],
            ['customer', self.customer3_scope_id],
        ])
