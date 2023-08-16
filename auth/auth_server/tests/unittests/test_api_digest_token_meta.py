import hashlib
import json
from auth.auth_server.models.models import Type, User
from auth.auth_server.models.models import gen_salt
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import hash_password


class TestAllowedActionsApi(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version)
        self.partner_scope_id = 'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d'
        self.customer1_scope_id = '19a00828-fbff-4318-8291-4b6c14a8066d'
        admin_user = self.create_root_user()
        session = self.db_session
        type_partner = Type(id=10, name='partner', parent=admin_user.type)
        type_customer = Type(id=20, name='customer', parent=type_partner)
        type_group = Type(id=30, name='group', parent=type_customer)
        salt = gen_salt()
        self.user_partner_password = 's0mepassWD!!1112'
        self.user_partner = User(
            'partner@domain.com', type=type_partner,
            password=hash_password(
                self.user_partner_password, salt),
            display_name='Partner user', scope_id=self.partner_scope_id,
            salt=salt, type_id=type_partner.id)
        self.user_customer = User(
            'user@domain.com', type=type_customer,
            password=hash_password(
                self.user_partner_password, salt),
            display_name='Customer user', scope_id=self.customer1_scope_id,
            salt=salt, type_id=type_customer.id)
        session.add(type_partner)
        session.add(type_customer)
        session.add(type_group)
        session.add(self.user_partner)
        session.add(self.user_customer)
        session.commit()

    def test_digest_get_token_metadata1(self):
        token_response = self.get_token_response(self.user_partner.email,
                                                 self.user_partner_password)
        token = token_response['token']
        digest = hashlib.md5(token.encode('utf-8')).hexdigest()
        code, token_meta = self.client.token_meta_get([digest])
        self.assertEqual(code, 200)
        self.assertEqual(len(token_meta), 1)
        self.assertEqual(token_meta[digest]['user_id'], self.user_partner.id)
        self.assertEqual(token_meta[digest]['user_name'],
                         self.user_partner.email)
        self.assertEqual(token_meta[digest]['user_display_name'],
                         self.user_partner.display_name)
        self.assertEqual(token_meta[digest]['ip'],
                         token_response['ip'])
        self.assertEqual(token_meta[digest]['token_created'],
                         token_response['created_at'])

    def test_digest_get_token_metadata_bulk(self):
        token_response1 = self.get_token_response(self.user_partner.email,
                                                  self.user_partner_password)
        token_response2 = self.get_token_response(self.user_customer.email,
                                                  self.user_partner_password)
        token1 = token_response1['token']
        token2 = token_response2['token']
        digest1 = hashlib.md5(token1.encode('utf-8')).hexdigest()
        digest2 = hashlib.md5(token2.encode('utf-8')).hexdigest()
        code, token_meta = self.client.token_meta_get([digest1, digest2])
        self.assertEqual(code, 200)
        self.assertEqual(len(token_meta), 2)
        self.assertEqual(token_meta[digest1]['user_id'], self.user_partner.id)
        self.assertEqual(token_meta[digest1]['user_name'],
                         self.user_partner.email)
        self.assertEqual(token_meta[digest1]['user_display_name'],
                         self.user_partner.display_name)
        self.assertEqual(token_meta[digest1]['ip'],
                         token_response1['ip'])
        self.assertEqual(token_meta[digest1]['token_created'],
                         token_response1['created_at'])
        self.assertEqual(token_meta[digest2]['user_id'], self.user_customer.id)
        self.assertEqual(token_meta[digest2]['user_name'],
                         self.user_customer.email)
        self.assertEqual(token_meta[digest2]['user_display_name'],
                         self.user_customer.display_name)
        self.assertEqual(token_meta[digest2]['ip'],
                         token_response2['ip'])
        self.assertEqual(token_meta[digest2]['token_created'],
                         token_response2['created_at'])

    def test_digest_get_with_unexpected(self):
        token = self.get_token(self.user_partner.email,
                               self.user_partner_password)
        digest = hashlib.md5(token.encode('utf-8')).hexdigest()
        payload_dict = {
            'digests': [digest]
        }
        body = {
            "payload": json.dumps(payload_dict),
            "parameter": 'value'
        }
        code, token_meta = self.client.get('digests', body)
        self.assertEqual(code, 400)
        self.assertEqual(token_meta['error']['reason'],
                         "Unexpected parameters: parameter")
