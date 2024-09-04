from datetime import datetime, timedelta
from freezegun import freeze_time
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.models.models import Type, VerificationCode
from auth.auth_server.utils import get_digest


class TestVerificationCodeApi(TestAuthBase):
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

    def test_create(self):
        verification_code = 123456
        dt = datetime(2024, 2, 2, 10)
        with freeze_time(dt):
            code, response = self.client.verification_code_create(
                self.admin_user.email, verification_code)
            self.assertEqual(code, 201)
            self.assertEqual(response['code'],
                             get_digest(str(verification_code)))
            self.assertEqual(response['valid_until'], '2024-02-02T11:00:00')

    def test_invalid_parameters(self):
        code, response = self.client.verification_code_create(
            None, 123456)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OA0032')
        self.assertEqual(response['error']['params'], ['email'])

        code, response = self.client.verification_code_create(
            'notexist@email.com', 123456)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OA0037')

        code, response = self.client.verification_code_create(
            self.admin_user.email, None)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['params'], ['code'])

    def test_invalidation(self):
        code_1 = 1
        dt = datetime.utcnow()
        with freeze_time(dt):
            _, verification_code_1 = self.client.verification_code_create(
                self.admin_user.email, code_1)
        code_2 = 2
        with freeze_time(dt + timedelta(minutes=1, seconds=1)):
            _, verification_code_2 = self.client.verification_code_create(
                self.admin_user.email, code_2)
        code_3 = 3
        with freeze_time(dt + timedelta(minutes=2, seconds=2)):
            _, verification_code_3 = self.client.verification_code_create(
                self.admin_user.email, code_3)

        verification_codes = self.db_session.query(VerificationCode).all()
        codes_deleted_at_map = {
            x.code: x.deleted_at for x in verification_codes
        }
        self.assertNotEqual(codes_deleted_at_map[get_digest(str(code_1))], 0)
        self.assertNotEqual(codes_deleted_at_map[get_digest(str(code_2))], 0)
        self.assertEqual(codes_deleted_at_map[get_digest(str(code_3))], 0)

    def test_create_unexpected(self):
        code, resp = self.client.post('verification_codes', {
            'email': self.admin_user.email,
            'code': 1234,
            'asd': '213'
        })
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0022')
        self.assertEqual(resp['error']['params'], ['asd'])

    def test_create_immutable(self):
        for field in ['id', 'deleted_at', 'created_at', 'valid_until']:
            code, resp = self.client.post('verification_codes', {
                'email': self.admin_user.email,
                'code': 1234,
                field: 12345
            })
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OA0021')
            self.assertEqual(resp['error']['params'], [field])

    def test_generation_time_threshold(self):
        dt = datetime.utcnow()
        with freeze_time(dt):
            code, _ = self.client.verification_code_create(
                self.admin_user.email, 1)
        self.assertEqual(code, 201)
        with freeze_time(dt + timedelta(minutes=1)):
            code, resp = self.client.verification_code_create(
                self.admin_user.email, 1)
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0072')

        with freeze_time(dt + timedelta(minutes=1, seconds=1)):
            code, _ = self.client.verification_code_create(
                self.admin_user.email, 1)
        self.assertEqual(code, 201)
