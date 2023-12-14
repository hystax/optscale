import os
from unittest.mock import patch

from auth.auth_server.models.models import (Type, User, Role, Assignment,
                                            Action, ActionGroup)
from auth.auth_server.models.models import gen_salt
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import hash_password


class TestSignIn(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version=version)
        self.partner_scope_id = 'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d'
        self.customer1_scope_id = '19a00828-fbff-4318-8291-4b6c14a8066d'
        self.group11_scope_id = 'be7b4d5e-33b6-40aa-bc6a-00c7d822606f'
        self.hierarchy = (
            {'root': {'null': {'partner': {
                'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d':
                    {'customer': {
                        '19a00828-fbff-4318-8291-4b6c14a8066d':
                            {'group': ['be7b4d5e-33b6-40aa-bc6a-00c7d822606f']
                             },
                    }},
            }}}}
        )
        admin_user = self.create_root_user()
        session = self.db_session
        type_partner = Type(id_=10, name='partner', parent=admin_user.type)
        type_customer = Type(id_=20, name='customer', parent=type_partner)
        type_group = Type(id_=30, name='group', parent=type_customer)
        self.user_type_id = int(type_group.id)
        salt = gen_salt()
        user_partner = User(
            'partner@domain.com', type_=type_partner,
            password=hash_password('passwd!!!111', salt),
            display_name='Partner user', scope_id=self.partner_scope_id,
            salt=salt, type_id=type_partner.id)
        self.user_customer_email = 'customer@domain.com'
        self.user_customer_password = 'p@sswRD!'
        self.user_customer_name = 'Customer user'
        user_customer = User(
            self.user_customer_email, type_=type_customer,
            salt=salt,
            display_name=self.user_customer_name,
            password=hash_password(
                self.user_customer_password, salt),
            scope_id=self.customer1_scope_id, type_id=type_customer.id)

        user_action_group = ActionGroup(name='Manage users and assignments')
        # admin action has type=root
        action_list_users = Action(name='LIST_USERS', type_=type_customer,
                                   action_group=user_action_group)
        action_create_user = Action(name='CREATE_USER',
                                    type_=type_customer,
                                    action_group=user_action_group)
        action_edit_user_info = Action(name='EDIT_USER_INFO',
                                       type_=type_customer,
                                       action_group=user_action_group)
        action_delete_user = Action(name='DELETE_USER', type_=admin_user.type,
                                    action_group=user_action_group)
        action_activate_user = Action(name='ACTIVATE_USER',
                                      type_=type_customer,
                                      action_group=user_action_group)
        action_reset_password = Action(name='RESET_USER_PASSWORD',
                                       type_=type_customer,
                                       action_group=user_action_group)
        admin_role = Role(name='ADMIN', type_=type_customer, lvl=type_customer,
                          scope_id=self.customer1_scope_id,
                          description='Admin')
        partner1_nodelete_role = Role(name='P1 No delete', type_=type_partner,
                                      lvl=type_customer,
                                      scope_id=self.partner_scope_id)
        partner1_delete_role = Role(name='P1 User Deleter', type_=type_partner,
                                    lvl=type_customer)
        session.add(type_partner)
        session.add(type_customer)
        session.add(type_group)
        session.add(user_partner)
        session.add(user_customer)
        session.add(action_list_users)
        session.add(action_create_user)
        session.add(action_edit_user_info)
        session.add(action_delete_user)
        session.add(action_activate_user)
        session.add(action_reset_password)
        session.add(admin_role)
        session.add(partner1_nodelete_role)
        session.add(partner1_delete_role)
        admin_role.assign_action(action_list_users)
        admin_role.assign_action(action_create_user)
        admin_role.assign_action(action_edit_user_info)
        admin_role.assign_action(action_delete_user)
        admin_role.assign_action(action_activate_user)
        admin_role.assign_action(action_reset_password)
        partner1_nodelete_role.assign_action(action_list_users)
        partner1_nodelete_role.assign_action(action_create_user)
        partner1_delete_role.assign_action(action_create_user)
        partner1_delete_role.assign_action(action_delete_user)
        assignment = Assignment(user_customer, admin_role,
                                type_customer, self.customer1_scope_id)
        assignment_p_c1 = Assignment(user_partner, partner1_nodelete_role,
                                     type_customer, self.customer1_scope_id)
        assignment_p_c1_del = Assignment(user_partner, partner1_delete_role,
                                         type_partner, self.partner_scope_id)

        session.add(assignment)
        session.add(assignment_p_c1)
        session.add(assignment_p_c1_del)
        session.commit()
        self.client.token = self.get_token(user_customer.email,
                                           self.user_customer_password)

    def test_signin_not_provided(self):
        for prop in ['token', 'provider']:
            code, resp = self.client.post(
                self.client.signin_url(), {prop: 'val'})
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OA0031')

    def test_signin_unexpected(self):
        code, resp = self.client.post(
            self.client.signin_url(),
            {'provider': 'provider', 'token': 'token', 'aza': 'az'})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0022')

    def test_signin_unsupported_provider(self):
        code, resp = self.client.signin(provider='provider', token='token')
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0067')

    def test_signin_token_length(self):
        code, resp = self.client.signin(
            provider='provider', token='t' * 70000)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0048')

    def test_signin_token_whitespaces(self):
        payload = {'provider': 'provider', 'token': 'token'}
        for prop in ['provider', 'token']:
            body = payload.copy()
            body[prop] = '   '
            code, resp = self.client.signin(**body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OA0065')

    def test_signin_invalid_request_body(self):
        code, resp = self.client.post(self.client.signin_url(), '{"test": %}')
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['reason'],
                         'Incorrect request body received')

    def test_signin_no_client_id(self):
        code, _ = self.client.post(
            self.client.signin_url(),
            {'provider': 'google', 'token': 'token'})
        self.assertEqual(code, 403)

    @patch.dict(os.environ, {'GOOGLE_OAUTH_CLIENT_ID': '223322'}, clear=True)
    def test_signin_invalid_token(self):
        with patch('google.oauth2.id_token.verify_oauth2_token',
                   side_effect=ValueError):
            code, _ = self.client.signin(provider='google', token='token')
            self.assertEqual(code, 403)

    @patch.dict(os.environ, {'GOOGLE_OAUTH_CLIENT_ID': '223322'}, clear=True)
    def test_signin_google_non_verified_email(self):
        token_info = {'email': 'test@domain.com', 'name': 'John Doe'}
        with patch('google.oauth2.id_token.verify_oauth2_token',
                   return_value=token_info):
            code, _ = self.client.signin(provider='google', token='token')
            self.assertEqual(code, 403)

    @patch.dict(os.environ, {'GOOGLE_OAUTH_CLIENT_ID': '223322'}, clear=True)
    def test_signin_google_new_user(self):
        email = 'test@domain.com'
        name = 'John Doe'
        patch('auth.auth_server.controllers.user.UserController.'
              'domain_blacklist').start()
        patch('auth.auth_server.controllers.signin.GoogleOauth2Provider.'
              'exchange_token').start()
        token_info = {'email': email, 'name': name, 'email_verified': True}
        with patch('google.oauth2.id_token.verify_oauth2_token',
                   return_value=token_info):
            code, resp = self.client.signin(provider='google', token='token')
            self.assertEqual(code, 201)
            self.assertEqual(resp['user_email'], email)

            code, resp = self.client.user_get(resp['user_id'])
            self.assertEqual(code, 200)
            self.assertEqual(resp['email'], email)
            self.assertEqual(resp['display_name'], name)
            self.assertEqual(resp['is_password_autogenerated'], True)

    @patch.dict(os.environ, {'MICROSOFT_OAUTH_CLIENT_ID': '123'}, clear=True)
    def test_signin_azure_new_user(self):
        email = 'test@domain.com'
        name = 'John Doe'
        patch('auth.auth_server.controllers.user.UserController.'
              'domain_blacklist').start()
        token_info = (email, name)
        with patch('auth.auth_server.controllers.signin.'
                   'MicrosoftOauth2Provider.verify',
                   return_value=token_info):
            code, resp = self.client.signin(provider='microsoft',
                                            token='token')
        self.assertEqual(code, 201)
        self.assertEqual(resp['user_email'], email)

        code, resp = self.client.user_get(resp['user_id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['email'], email)
        self.assertEqual(resp['display_name'], name)
        self.assertEqual(resp['is_password_autogenerated'], True)

    @patch.dict(os.environ, {'GOOGLE_OAUTH_CLIENT_ID': '223322'}, clear=True)
    def test_signin_existing_user(self):
        patch('auth.auth_server.controllers.user.UserController.'
              'domain_blacklist').start()
        token_info = (self.user_customer_email, self.user_customer_name)
        with patch('auth.auth_server.controllers.signin.'
                   'GoogleOauth2Provider.verify',
                   return_value=token_info):
            code, resp = self.client.signin(provider='google', token='token')
        self.assertEqual(code, 201)
        self.assertEqual(resp['user_email'], self.user_customer_email)

    @patch.dict(os.environ, {'MICROSOFT_OAUTH_CLIENT_ID': '123'}, clear=True)
    def test_signin_existing_user_ms(self):
        patch('auth.auth_server.controllers.user.UserController.'
              'domain_blacklist').start()
        token_info = (self.user_customer_email, self.user_customer_name)
        with patch('auth.auth_server.controllers.signin.'
                   'MicrosoftOauth2Provider.verify',
                   return_value=token_info):
            code, resp = self.client.signin(provider='microsoft',
                                            token='token')
        self.assertEqual(code, 201)
        self.assertEqual(resp['user_email'], self.user_customer_email)
