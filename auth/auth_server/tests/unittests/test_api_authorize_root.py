import uuid
from unittest.mock import patch
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.models.models import (Type, User, Role, Assignment,
                                            Action, ActionGroup)
from auth.auth_server.models.models import gen_salt
from auth.auth_server.utils import hash_password


class TestAuthorize(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version=version)
        self.partner1_scope_id = 'db8e7d80-5d71-4d11-8283-b90d8c403049'
        self.context1 = {
            "partner": self.partner1_scope_id,
        }
        self.partner2_scope_id = '3f4a7b7e-9c8e-4aa2-86b8-792388fa45ab'
        self.context2 = {
            "partner": self.partner2_scope_id,
        }
        session = self.db_session
        type_root = Type(id_=0, name='root')
        type_partner = Type(id_=10, name='partner', parent=type_root)
        type_customer = Type(id_=20, name='customer', parent=type_partner)
        self.root_user_pass = 'R00tpassword1'
        root_salt = gen_salt()
        user_root = User(
            'root@allcom.com', type_=type_root,
            password=hash_password(self.root_user_pass, root_salt),
            display_name='I\'m Root!', scope_id=None, salt=root_salt
        )
        partner1_salt = gen_salt()
        self.partner1_password = 'p4sswOrd111'
        user_partner1 = User(
            'partner1@allcom.com', type_=type_partner,
            password=hash_password(self.partner1_password, partner1_salt),
            scope_id=self.partner1_scope_id, display_name='Awesome partner',
            type_id=type_partner.id, salt=partner1_salt)
        partner2_salt = gen_salt()
        self.partner2_password = 'PASSwoRD1123444'
        user_partner2 = User(
            'partner2@allcom.com', type_=type_partner,
            password=hash_password(self.partner2_password,
                                   partner2_salt),
            salt=partner2_salt,
            scope_id=self.partner2_scope_id,
            display_name='Not awesome partner', type_id=type_partner.id)
        user_backup_agent = User(
            'customer@allcom.com', type_=type_customer, password='my-pass',
            display_name='Agent Smith',
            scope_id=str(uuid.uuid4())
        )
        self.root_user_email = str(user_root.email)
        self.partner1_user_email = str(user_partner1.email)
        self.partner2_user_email = str(user_partner2.email)
        manage_customers_group = ActionGroup(name='Manage customers')
        cs_action_group = ActionGroup(name='cloudsite')
        backup_action_group = ActionGroup(name='protection')
        # admin action has type=root
        create_customer_action = Action(name='CREATE_CUSTOMER',
                                        type_=type_root,
                                        action_group=manage_customers_group)
        create_cs_action = Action(name='CREATE_CS', type_=type_partner,
                                  action_group=cs_action_group)
        create_backup_action = Action(name='CREATE_BACKUP',
                                      type_=type_customer,
                                      action_group=backup_action_group)
        role_scope_id = str(uuid.uuid4())
        admin_role = Role(name='ADMIN', type_=type_partner, lvl=type_customer,
                          scope_id=role_scope_id, description='Admin')
        operator_role = Role(name='Operator', type_=type_partner,
                             lvl=type_customer, scope_id=role_scope_id,
                             description='Cloud operator')
        backup_operator_role = Role(name='Backup Operator',
                                    type_=type_customer,
                                    lvl=type_customer, scope_id=role_scope_id,
                                    description='Backup Operator')
        session.add(type_root)
        session.add(type_partner)
        session.add(type_customer)
        session.add(user_root)
        session.add(user_partner1)
        session.add(user_partner2)
        session.add(user_backup_agent)
        session.add(manage_customers_group)
        session.add(cs_action_group)
        session.add(backup_action_group)
        session.add(create_customer_action)
        session.add(create_cs_action)
        session.add(create_backup_action)
        session.add(admin_role)
        session.add(operator_role)
        session.add(backup_operator_role)
        admin_role.assign_action(create_customer_action)
        admin_role.assign_action(create_cs_action)
        admin_role.assign_action(create_backup_action)
        operator_role.assign_action(create_cs_action)
        assignment_p1 = Assignment(user_partner1, admin_role, type_partner,
                                   self.partner1_scope_id)
        assigment_p2 = Assignment(user_partner2, operator_role, type_partner,
                                  self.partner2_scope_id)
        assigment_root = Assignment(user_root, admin_role, type_root, None)
        assigment_backup_admin = Assignment(user_backup_agent,
                                            backup_operator_role,
                                            type_customer,
                                            user_backup_agent.scope_id)
        session.add(assignment_p1)
        session.add(assigment_p2)
        session.add(assigment_root)
        session.add(assigment_backup_admin)
        session.commit()
        self.assignment_p1_id = assignment_p1.id
        self.assignment_p2_id = assigment_p2.id
        self.assignment_root_id = assigment_root.id

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_admin_notoken(self, p_get_context):
        p_get_context.return_value = self.context1
        code, _ = self.client.authorize('CREATE_CUSTOMER', 'partner',
                                        self.partner1_scope_id)
        self.assertEqual(code, 401)

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_admin_partner1(self, p_get_context):
        p_get_context.return_value = self.context1
        self.client.token = self.get_token(self.partner1_user_email,
                                           self.partner1_password)
        code, auth = self.client.authorize('CREATE_CUSTOMER', 'partner',
                                           self.partner1_scope_id)
        self.assertEqual(code, 200)
        self.assertTrue(any(map(lambda x: x['id'] in self.assignment_p1_id,
                                auth['assignments'])))

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_create_cs_partner2(self, p_get_context):
        p_get_context.return_value = self.context2
        self.client.token = self.get_token(self.partner2_user_email,
                                           self.partner2_password)
        code, auth = self.client.authorize('CREATE_CS', 'partner',
                                           self.partner2_scope_id)
        self.assertEqual(code, 200)
        self.assertTrue(any(map(lambda x: x['id'] in self.assignment_p2_id,
                                auth['assignments'])))

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_admin_partner2(self, p_get_context):
        p_get_context.return_value = self.context2
        self.client.token = self.get_token(self.partner2_user_email,
                                           self.partner2_password)
        code, _ = self.client.authorize('CREATE_CUSTOMER', 'partner',
                                        self.partner2_scope_id)
        self.assertEqual(code, 403)

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_admin_invalid_scope_partner1(self, p_get_context):
        p_get_context.return_value = self.context1
        self.client.token = self.get_token(self.partner1_user_email,
                                           self.partner1_password)
        code, _ = self.client.authorize('CREATE_CUSTOMER', 'partner',
                                        self.partner2_scope_id)
        self.assertEqual(code, 403)

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_root_resources_partner1(self, p_get_context):
        p_get_context.return_value = self.context1
        self.client.token = self.get_token(self.root_user_email,
                                           self.root_user_pass)
        code, auth = self.client.authorize('CREATE_CUSTOMER', 'partner',
                                           None)
        self.assertEqual(code, 200)
        self.assertTrue(any(map(lambda x: x['id'] in self.assignment_root_id,
                                auth['assignments'])))

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_root_resources_partner2(self, p_get_context):
        p_get_context.return_value = self.context2
        self.client.token = self.get_token(self.root_user_email,
                                           self.root_user_pass)
        code, auth = self.client.authorize('CREATE_CUSTOMER', 'partner',
                                           None)
        self.assertEqual(code, 200)
        self.assertTrue(any(map(lambda x: x['id'] in self.assignment_root_id,
                                auth['assignments'])))

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_root_create_cs_resources_partner(self, p_get_context):
        p_get_context.return_value = self.context2
        self.client.token = self.get_token(self.root_user_email,
                                           self.root_user_pass)
        code, auth = self.client.authorize('CREATE_CS', 'partner',
                                           None)
        self.assertEqual(code, 200)
        self.assertTrue(any(map(lambda x: x['id'] in self.assignment_root_id,
                                auth['assignments'])))

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_root_as_backup_agent(self, p_get_context):
        p_get_context.return_value = {}
        self.client.token = self.get_token(self.root_user_email,
                                           self.root_user_pass)
        code, auth = self.client.authorize('CREATE_BACKUP', 'customer',
                                           None)
        self.assertEqual(code, 200)
        self.assertTrue(any(map(lambda x: x['id'] in self.assignment_root_id,
                                auth['assignments'])))
