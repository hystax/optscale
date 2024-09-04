from datetime import datetime, timedelta
import uuid
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.models.models import (Type, User, gen_salt,
                                            VerificationCode)
from auth.auth_server.utils import hash_password, get_digest
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
                f'Parameter "{immutable_parameter}" is immutable')

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
                f'Unexpected parameters: {unexpected_parameter}')

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

    def test_token_by_verification_code(self):
        session = self.db_session
        partner_salt = gen_salt()
        partner_password = 'pass1234'
        partner_email = 'partner@mail.com'
        partner_user = User(
            partner_email, self.type_customer, display_name='Partner User',
            password=hash_password(partner_password, partner_salt),
            scope_id=str(uuid.uuid4()), salt=partner_salt)
        session.add(partner_user)

        code_1, code_3, code_4 = 123456, 234567, 345678
        now = datetime.utcnow()
        vc_1 = VerificationCode(
            email='wrong@email.com', valid_until=now + timedelta(hours=1),
            code=get_digest(str(code_1)))
        vc_2 = VerificationCode(
            email=partner_email, valid_until=now + timedelta(hours=1),
            code=get_digest('112345'))
        vc_3 = VerificationCode(
            email=partner_email, valid_until=now - timedelta(seconds=1),
            code=get_digest(str(code_3)))
        vc_4 = VerificationCode(
            email=partner_email, valid_until=now + timedelta(minutes=1),
            code=get_digest(str(code_4)))
        for vc in [vc_1, vc_2, vc_3, vc_4]:
            session.add(vc)
        session.commit()

        self.client.secret = None
        for code in [code_1, code_3]:
            body = {
                'verification_code': code,
                'email': partner_user.email,
            }
            code, resp = self.client.post('tokens', body)
            self.assertEqual(code, 403)
            self.assertEqual(resp['error']['error_code'], 'OA0071')

        body = {
            'verification_code': code_4,
            'email': partner_user.email,
        }
        code, resp = self.client.post('tokens', body)
        self.assertEqual(code, 201)
        self.assertEqual(resp['user_email'], partner_user.email)
        self.assertTrue(vc_4.deleted_at != 0)
