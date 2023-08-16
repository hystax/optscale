from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.models.models import *
from auth.auth_server.controllers.token import xstr
from auth.auth_server.utils import hash_password
from auth.auth_server.tests.unittests.utils import extract_caveats


class TestTokenApi(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version)
        self.admin_user_password = 'toor'
        self.admin_user = self.create_root_user(
            password=self.admin_user_password)
        session = self.db_session
        name_partner = 'partner'
        name_customer = 'customer'
        self.type_partner = Type(name=name_partner,
                                 parent=self.admin_user.type)
        self.type_customer = Type(name=name_customer, parent=self.type_partner)
        session.add(self.admin_user)
        session.add(self.type_partner)
        session.add(self.type_customer)

    def test_get_token_root(self):
        session = self.db_session
        session.commit()
        extract_caveats(self.get_token(self.admin_user.email,
                                       self.admin_user_password))

    def test_get_token_partner(self):
        session = self.db_session
        partner_salt = gen_salt()
        partner_password = 'P@ssW0rd111'
        partner_user = User('partner@mail.com', self.type_customer,
                            hash_password(partner_password, partner_salt),
                            display_name='Partner User',
                            scope_id=str(uuid.uuid4()),
                            salt=partner_salt)
        session.add(partner_user)
        session.commit()
        extract_caveats(self.get_token(partner_user.email,
                                       partner_password))

    def test_get_token_with_immutables(self):
        session = self.db_session
        partner_salt = gen_salt()
        partner_password = 'P@ssW0rd111'
        partner_user = User('partner@mail.com', self.type_customer,
                            hash_password(partner_password, partner_salt),
                            display_name='Partner User',
                            scope_id=str(uuid.uuid4()),
                            salt=partner_salt)
        session.add(partner_user)
        session.commit()
        for immutable_parameter in ['user_id', 'ip', 'created_at',
                                    'valid_until', 'digest']:
            body = {
                'email': partner_user.email,
                'password': partner_password,
                immutable_parameter: 'value'
            }
            self.client.secret = None
            code, token = self.client.post('tokens', body)
            self.assertEqual(code, 400)
            self.assertEqual(
                token['error']['reason'],
                'Parameter "%s" is immutable' % immutable_parameter)

    def test_get_token_with_unexpected(self):
        session = self.db_session
        partner_salt = gen_salt()
        partner_password = 'P@ssW0rd111'
        partner_user = User('partner@mail.com', self.type_customer,
                            hash_password(partner_password, partner_salt),
                            display_name='Partner User',
                            scope_id=str(uuid.uuid4()),
                            salt=partner_salt)
        session.add(partner_user)
        session.commit()
        for unexpected_parameter in ['param', '', 9, 'token']:
            body = {
                'email': partner_user.email,
                'password': partner_password,
                unexpected_parameter: 'value'
            }
            self.client.secret = None
            code, token = self.client.post('tokens', body)
            self.assertEqual(code, 400)
            self.assertEqual(
                token['error']['reason'],
                'Unexpected parameters: %s' % unexpected_parameter)

    def test_not_allowed_method(self):
        code, response = self.client.get('tokens', {})
        self.assertEqual(code, 405)
        self.assertEqual(response['error']['reason'], 'GET method not allowed')

    def test_get_token_not_existent_user(self):
        self.client.secret = None
        code, token = self.client.token_get('notexistent@mail.com', 'pass')
        self.assertEqual(code, 403)
        self.assertEqual(token['error']['reason'],
                         'Email or password is invalid')

    def test_get_token_cluster_secret(self):
        session = self.db_session
        session.commit()

        code, token_info = self.client.token_get_user_id(self.admin_user.id)
        self.assertEqual(code, 201)
        self.assertEqual(token_info['user_email'], self.admin_user.email)
        extract_caveats(token_info['token'])
