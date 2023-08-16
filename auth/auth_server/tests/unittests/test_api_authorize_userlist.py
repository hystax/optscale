from unittest import mock
from unittest.mock import patch

from requests import HTTPError

from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.models.models import (Type, User, Action, Role, Assignment,
                                            ActionGroup)
from auth.auth_server.models.models import gen_salt
from auth.auth_server.utils import hash_password


class TestAuthorizeUserlistApi(TestAuthBase):
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
                self.partner_scope_id:
                    {'customer': {
                        self.customer1_scope_id:
                            {'group': ['be7b4d5e-33b6-40aa-bc6a-00c7d822606f']
                             },
                        self.customer2_scope_id:
                            {'group': ['e8b8b4e9-a92d-40b5-a5db-b38bf5314ef9',
                                       '42667dde-0427-49be-9541-8e99362ee96e']
                             },
                    }},
                self.partner2_scope_id:
                    {'customer': {
                        self.customer3_scope_id:
                            {'group': [self.group3_scope_id]
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
            'partner@somedomain.com', type=self.type_partner,
            password=hash_password(
                self.user_partner_password, user_partner_salt),
            display_name='Partner user', scope_id=self.partner_scope_id,
            salt=user_partner_salt, type_id=self.type_partner.id)
        self.user_customer = User(
            'user@somedomain.com', type=self.type_customer,
            password=hash_password(
                self.user_partner_password, user_partner_salt),
            display_name='Customer user', scope_id=self.customer3_scope_id,
            salt=user_partner_salt, type_id=self.type_customer.id)

        devices_action_group = ActionGroup(name='MANAGE_DEVICES')
        role_action_cloudsites = ActionGroup(name='MANAGE_CLOUDSITES')
        custom_action_group = ActionGroup(name='CUSTOM_ACTIONS')

        action_create_device = Action(name='CREATE_DEVICE',
                                      type=self.type_group,
                                      action_group=devices_action_group)
        action_managec_cs = Action(name='MANAGE_CLOUDSITES',
                                   type=self.type_customer,
                                   action_group=role_action_cloudsites)
        action_custom1 = Action(name='CUSTOM_ACTION1',
                                type=self.type_customer,
                                action_group=custom_action_group)
        action_custom2 = Action(name='CUSTOM_ACTION2',
                                type=self.type_customer,
                                action_group=custom_action_group)
        action_custom3 = Action(name='CUSTOM_ACTION3',
                                type=self.type_customer,
                                action_group=custom_action_group)

        self.admin_role = Role(name='ADMIN', type=self.type_partner,
                               lvl=self.type_customer,
                               scope_id=self.partner_scope_id,
                               description='Admin',
                               shared=True)

        self.role_lvl_customer = Role(
            name='customer_role', type=self.type_customer,
            lvl=self.type_customer, scope_id=self.customer1_scope_id,
            description='')

        self.role_custom = Role(
            name='custom_role', type=self.type_customer,
            lvl=self.type_customer, scope_id=self.customer3_scope_id,
            description='Some custom role')

        session.add(self.type_partner)
        session.add(self.type_customer)
        session.add(self.type_group)
        session.add(self.user_partner)
        session.add(self.user_customer)

        session.add(self.admin_role)
        session.add(self.role_lvl_customer)
        session.add(self.role_custom)

        self.admin_role.assign_action(action_create_device)
        self.admin_role.assign_action(action_managec_cs)
        self.role_custom.assign_action(action_custom1)
        self.role_custom.assign_action(action_custom2)
        self.role_custom.assign_action(action_custom3)

        assignment_admin = Assignment(self.admin_user, self.admin_role,
                                      self.admin_user.type, None)

        assignment_partner = Assignment(
            self.user_partner, self.admin_role, self.type_partner,
            self.partner_scope_id)

        assignment_customer3 = Assignment(
            self.user_customer, self.admin_role, self.type_customer,
            self.customer3_scope_id
        )
        assignment_custom_role_customer3 = Assignment(
            self.user_customer, self.role_custom, self.type_customer,
            self.customer3_scope_id
        )

        session.add(assignment_admin)
        session.add(assignment_partner)
        session.add(assignment_customer3)
        session.add(assignment_custom_role_customer3)
        session.commit()

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_case1(self, p_context):
        p_context.return_value = {
            "partner": self.partner_scope_id,
            "customer": self.customer1_scope_id,
        }
        code, response = self.client.authorize_user_list(
            [self.user_partner.id, self.user_customer.id],
            list(map(lambda x: x.name, self.admin_role.actions)),
            'customer', self.customer1_scope_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 2)
        self.assertEqual(response.get(self.user_customer.id), list())
        self.assertEqual(
            response.get(self.user_partner.id).sort(),
            list(map(lambda x: x.name, self.admin_role.actions)).sort())

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_case1_root_lvl(self, p_context):
        p_context.return_value = {}
        code, response = self.client.authorize_user_list(
            [self.admin_user.id],
            list(map(lambda x: x.name, self.admin_role.actions)),
            'customer', self.customer1_scope_id)
        self.assertEqual(code, 200)
        self.assertEqual(
            response.get(self.admin_user.id).sort(),
            list(map(lambda x: x.name, self.admin_role.actions)).sort())

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_case2_custom_actions(self, p_context):
        p_context.return_value = {
            "partner": self.partner2_scope_id,
            "customer": self.customer3_scope_id,
        }
        code, response = self.client.authorize_user_list(
            [self.user_customer.id],
            list(map(lambda x: x.name, self.role_custom.actions)),
            'customer', self.customer3_scope_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 1)
        self.assertEqual(
            response.get(self.user_customer.id).sort(),
            list(map(lambda x: x.name, self.role_custom.actions)).sort())

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_case2_admin_actions(self, p_context):
        p_context.return_value = {
            "partner": self.partner2_scope_id,
            "customer": self.customer3_scope_id,
        }
        code, response = self.client.authorize_user_list(
            [self.user_customer.id],
            list(map(lambda x: x.name, self.admin_role.actions)),
            'customer', self.customer3_scope_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 1)
        self.assertEqual(
            response.get(self.user_customer.id).sort(),
            list(map(lambda x: x.name, self.admin_role.actions)).sort())

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_invalid_scope_name(self, p_context):
        err_400 = HTTPError(mock.Mock(), 'bad request')
        err_400.response = mock.Mock(status_code=400, localized='OA0000')
        p_context.side_effect = err_400
        invalid_scope_name = 'unknown'
        code, response = self.client.authorize_user_list(
            [self.user_customer.id],
            list(map(lambda x: x.name, self.admin_role.actions)),
            invalid_scope_name, self.customer3_scope_id)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'], 'Invalid type %s' %
                         invalid_scope_name)

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_invalid_scope_id(self, p_context):
        err_404 = HTTPError(mock.Mock(), 'bad request')
        err_404.response = mock.Mock(status_code=404, localized='OA0000')
        p_context.side_effect = err_404
        invalid_scope_id = 'unknown'
        code, response = self.client.authorize_user_list(
            [self.user_customer.id],
            list(map(lambda x: x.name, self.admin_role.actions)),
            'customer', invalid_scope_id)
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['reason'], '%s %s not found' %
                         ('customer', invalid_scope_id))

    def test_invalid_user_list_type(self):
        code, response = self.client.authorize_user_list(
            'root',
            list(map(lambda x: x.name, self.admin_role.actions)),
            'customer', self.customer3_scope_id)
        self.assertEqual(code, 400)
        self.assertTrue('should be list' in response['error']['reason'])

    def test_invalid_action_list_type(self):
        code, response = self.client.authorize_user_list(
            [self.user_customer.id],
            'SOME_ACTION', 'customer', self.customer3_scope_id)
        self.assertEqual(code, 400)
        self.assertTrue('should be list' in response['error']['reason'])
