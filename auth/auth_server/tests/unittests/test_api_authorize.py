import uuid
from requests import HTTPError
from unittest.mock import patch
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.models.models import (Type, User, Role, Assignment,
                                            Action, ActionGroup)
from auth.auth_server.models.models import gen_salt
from auth.auth_server.utils import hash_password
from unittest import mock


class TestAuthorize(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version=version)

        self.partner_scope_id = 'ccf4b1a9-1989-455e-8247-f7e5d67c5105'
        self.customer_scope_id = '58185451-d3f4-433b-a4a2-b5506f550f46'
        self.context = {
            "partner": self.partner_scope_id,
            "customer": self.customer_scope_id,
        }
        self.admin_user_pass = 'aDmin_passw0rd'
        user_admin = self.create_root_user(password=self.admin_user_pass)
        session = self.db_session
        self.admin_user_email = str(user_admin.email)
        self.type_partner = Type(id=10, name='partner', parent=user_admin.type)
        type_customer = Type(id=20, name='customer', parent=self.type_partner)
        type_group = Type(id=30, name='group', parent=type_customer)
        salt = gen_salt()
        user_partner_password = 'partn33rp@sse00rD'
        user_partner = User('partner@domain.com', type=self.type_partner,
                            password=hash_password(user_partner_password,
                                                   salt),
                            display_name='Generic partner user',
                            salt=salt,
                            scope_id=self.partner_scope_id,
                            type_id=self.type_partner.id)
        self.user_customer_password = 'c4stom3r pasSw0RD!1'
        user_customer = User(
            'customer@domain.com', type=type_customer,
            password=hash_password(self.user_customer_password,
                                   salt),
            scope_id=self.customer_scope_id,
            salt=salt,
            display_name='Generic customer user', type_id=type_customer.id)
        self.user_operator_password = 'Op3R4tor!'
        self.user_operator = User(
            'op@domain.com', type=type_customer,
            password=hash_password(self.user_operator_password,
                                   salt),
            display_name='Generic operator user',
            salt=salt,
            scope_id=self.customer_scope_id
        )
        self.user_operator_email = self.user_operator.email
        group_action_group = ActionGroup('Manage device groups and '
                                         'replication settings')
        # admin action has type=root
        create_group_action = Action(name='CREATE_GROUP',
                                     type=user_admin.type,
                                     action_group=group_action_group)
        cs_action_group = ActionGroup('cloudsite')
        create_cs_action = Action(name='CREATE_CS', type=type_customer,
                                  action_group=cs_action_group)
        delete_cs_action = Action(name='DELETE_CS', type=type_customer,
                                  action_group=cs_action_group)
        role_scope_id = str(uuid.uuid4())
        admin_role = Role(name='ADMIN', type=type_customer, lvl=type_customer,
                               scope_id=role_scope_id, description='Admin')
        self.operator_role = Role(name='Operator', type=type_customer,
                                  lvl=type_customer, scope_id=role_scope_id,
                                  description='Cloud operator')
        session.add(self.type_partner)
        session.add(type_customer)
        session.add(type_group)
        session.add(user_partner)
        session.add(user_customer)
        session.add(group_action_group)
        session.add(cs_action_group)
        session.add(create_group_action)
        session.add(create_cs_action)
        session.add(delete_cs_action)
        session.add(admin_role)
        session.add(self.operator_role)
        admin_role.assign_action(create_group_action)
        admin_role.assign_action(create_cs_action)
        admin_role.assign_action(delete_cs_action)
        self.operator_role.assign_action(create_cs_action)
        self.operator_role.assign_action(delete_cs_action)
        assignment_admin = Assignment(user_customer, admin_role,
                                      type_customer, self.customer_scope_id)
        assignment_operator = Assignment(self.user_operator,
                                         self.operator_role, type_customer,
                                         self.customer_scope_id)
        assigment_partner_admin = Assignment(user_admin, admin_role,
                                             self.type_partner,
                                             self.partner_scope_id)

        session.add(assignment_admin)
        session.add(assignment_operator)
        session.add(assigment_partner_admin)
        session.commit()
        self.assignment_admin_id = str(assignment_admin.id)
        self.assignment_operator_id = str(assignment_operator.id)
        self.assignment_partner_id = str(assigment_partner_admin.id)

        self.client.token = self.get_token(
            user_customer.email, self.user_customer_password)

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_admin(self, p_get_context):
        p_get_context.return_value = self.context
        code, auth = self.client.authorize('CREATE_GROUP', 'customer',
                                           self.customer_scope_id)
        self.assertEqual(code, 200)
        self.assertTrue(any(map(lambda x: x['id'] in self.assignment_admin_id,
                                auth['assignments'])))

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_operator_create_cs(self, p_get_context):
        p_get_context.return_value = self.context
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)

        code, auth = self.client.authorize('CREATE_CS', 'customer',
                                           self.customer_scope_id)
        self.assertEqual(code, 200)
        self.assertTrue(any(map(
            lambda x: x['id'] in self.assignment_operator_id,
            auth['assignments'])))

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_operator_create_cs_role_inactive(self, p_get_context):

        session = self.db_session
        # Deactivated role - should be 403!
        self.operator_role.is_active = False
        session.add(self.operator_role)
        session.commit()
        p_get_context.return_value = self.context
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)

        code, auth = self.client.authorize('CREATE_CS', 'customer',
                                           self.customer_scope_id)
        self.assertEqual(code, 403)
        self.assertEqual(auth['error']['reason'], 'Forbidden!')

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_operator_create_cs_user_inactive(self, p_get_context):
        session = self.db_session
        p_get_context.return_value = self.context
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)
        # disable user
        self.user_operator.is_active = False
        session.add(self.user_operator)
        session.commit()
        # Deactivated user - should be 403!
        code, auth = self.client.authorize('CREATE_CS', 'customer',
                                           self.customer_scope_id)
        self.assertEqual(code, 403)
        self.assertEqual(auth['error']['reason'], 'Forbidden!')

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_operator_delete_cs(self, p_get_context):
        p_get_context.return_value = self.context
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)

        code, auth = self.client.authorize('DELETE_CS', 'customer',
                                           self.customer_scope_id)
        self.assertEqual(code, 200)
        self.assertTrue(any(map(
            lambda x: x['id'] in self.assignment_operator_id,
            auth['assignments'])))

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_operator_forbidden(self, p_get_context):
        p_get_context.return_value = self.context
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)

        code, auth = self.client.authorize('CREATE_CUSTOMER', 'customer',
                                           self.customer_scope_id)
        self.assertEqual(code, 403)
        self.assertEqual(auth['error']['reason'], 'Forbidden!')

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_admin_rootscope_forbidden(self, p_get_context):
        p_get_context.return_value = {
            "partner": self.partner_scope_id
        }
        code, auth = self.client.authorize('CREATE_GROUP', 'partner',
                                           self.partner_scope_id)
        self.assertEqual(code, 403)
        self.assertEqual(auth['error']['reason'], 'Forbidden!')

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_partner_admin(self, p_get_context):
        p_get_context.return_value = {
            "partner": self.partner_scope_id
        }
        self.client.token = self.get_token(self.admin_user_email,
                                           self.admin_user_pass)

        code, auth = self.client.authorize('CREATE_GROUP', 'partner',
                                           self.partner_scope_id)
        self.assertEqual(code, 200)
        self.assertTrue(any(map(
            lambda x: x['id'] in self.assignment_partner_id,
            auth['assignments'])))

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_partner_admin_delete_cs(self, p_get_context):
        p_get_context.return_value = self.context
        self.client.token = self.get_token(self.admin_user_email,
                                           self.admin_user_pass)

        code, auth = self.client.authorize('DELETE_CS', 'customer',
                                           self.customer_scope_id)
        self.assertEqual(code, 200)
        self.assertTrue(any(map(
            lambda x: x['id'] in self.assignment_partner_id,
            auth['assignments'])))

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_scope_below_context(self, p_get_context):
        p_get_context.return_value = self.context
        code, auth = self.client.authorize('CREATE_GROUP', 'dr_plan',
                                           str(uuid.uuid4()))
        self.assertEqual(code, 200)
        self.assertTrue(any(map(lambda x: x['id'] in self.assignment_admin_id,
                                auth['assignments'])))

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_unexpected(self, p_get_context):
        p_get_context.return_value = self.context
        self.client.token = self.get_token(self.admin_user_email,
                                           self.admin_user_pass)
        for unexpected_parameter in ['param', '', 9]:
            body = {
                "action": 'DELETE_CS',
                "resource_type": 'customer',
                "uuid": self.customer_scope_id,
                unexpected_parameter: 'value'
            }
            code, auth = self.client.post('authorize', body)
            self.assertEqual(code, 400)
            self.assertEqual(
                auth['error']['reason'],
                'Unexpected parameters: %s' % unexpected_parameter)
            self.assertEqual(auth['error']['error_code'], 'OA0022')
            self.assertEqual(
                auth['error']['params'], [str(unexpected_parameter)])

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_invalid_resource_type(self, p_get_context):

        err_400 = HTTPError(mock.Mock(), 'bad request')
        err_400.response = mock.Mock(status_code=400, localized='OA0000')
        p_get_context.side_effect = err_400
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)
        for resource_type in ['str', 123]:
            code, auth = self.client.authorize(
                'DELETE_CS', resource_type, self.customer_scope_id)
            self.assertEqual(code, 403)
            self.assertEqual(auth['error']['reason'], 'Forbidden!')

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_without_resource_type(self, p_get_context):
        p_get_context.return_value = self.context
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)
        body = {
            "action": 'DELETE_CS',
            "uuid": self.customer_scope_id
        }
        code, auth = self.client.post('authorize', body)
        self.assertEqual(code, 400)
        self.assertEqual(auth['error']['reason'], 'resource_type is required')

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_without_action(self, p_get_context):
        p_get_context.return_value = self.context
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)
        body = {
            "resource_type": 'customer',
            "uuid": self.customer_scope_id
        }
        code, auth = self.client.post('authorize', body)
        self.assertEqual(code, 400)
        self.assertEqual(auth['error']['reason'], 'action is required')

    def test_authorize_empty_uuid(self):
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)
        code, auth = self.client.authorize(
            'DELETE_CS', 'customer', '')
        self.assertEqual(code, 400)
        self.assertEqual(auth['error']['reason'], 'Invalid scope_id')

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_root_without_scope(self, p_get_context):
        p_get_context.return_value = self.context
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)
        code, auth = self.client.authorize(
            'DELETE_CS', 'root')
        self.assertEqual(code, 200)

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_without_uuid(self, p_get_context):
        p_get_context.return_value = {}
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)
        body = {
            "resource_type": 'partner',
            "action": 'CREATE_CS',
        }
        code, auth = self.client.post('authorize', body)
        self.assertEqual(code, 403)

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_root_without_uuid(self, p_get_context):
        p_get_context.return_value = self.context
        self.client.token = self.get_token(self.user_operator_email,
                                           self.user_operator_password)
        body = {
            "resource_type": 'root',
            "action": 'CREATE_CS',
        }
        code, auth = self.client.post('authorize', body)
        self.assertEqual(code, 200)

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def test_authorize_partner_with_children(self, p_get_context):
        child_partner_scope_id = '471f24ea-288a-4457-b567-67bddbc49591'
        p_get_context.return_value = {
            "partner": [child_partner_scope_id, self.partner_scope_id]
        }
        salt = gen_salt()
        password = 'secret_pass'
        email = 'partner2@email.com'
        session = self.db_session
        child_partner = User(email, type=self.type_partner,
                             password=hash_password(password, salt),
                             display_name='Another partner',
                             salt=salt,
                             scope_id=child_partner_scope_id,
                             type_id=self.type_partner.id)
        session.add(child_partner)
        session.commit()

        self.client.token = self.get_token(email, password)

        code, auth = self.client.authorize('CREATE_GROUP', 'partner',
                                           child_partner_scope_id)
        self.assertEqual(code, 403)

        self.client.token = self.get_token(self.admin_user_email,
                                           self.admin_user_pass)
        code, auth = self.client.authorize('CREATE_GROUP', 'partner',
                                           child_partner_scope_id)
        self.assertEqual(code, 200)
