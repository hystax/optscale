from auth.auth_server.tests.unittests.test_model_base import TestModelBase
from auth.auth_server.auth_token.macaroon import MacaroonToken
from auth.auth_server.models.models import *
from auth.auth_server.tests.unittests.utils import extract_caveats


# Keeping this to track approximate token length
TOKEN_MAX_LEN = 400


class TestToken(TestModelBase):

    def setUp(self):
        super().setUp()
        session = self.db_session
        name_root = 'root'
        name_partner = 'partner'
        name_customer = 'customer'
        name_group = 'group'
        self.type_root = Type(name=name_root)
        self.type_partner = Type(name=name_partner, parent=self.type_root)
        self.type_customer = Type(name=name_customer, parent=self.type_partner)
        self.type_group = Type(name=name_group, parent=self.type_customer)
        session.add(self.type_root)
        session.add(self.type_partner)
        session.add(self.type_customer)
        session.add(self.type_group)

    def _check_token(self, user):
        session = self.db_session
        session.add(user)
        session.commit()
        register = str(False)
        provider = 'optscale'
        macaroon_token = MacaroonToken(user.salt, user.id)
        token = macaroon_token.create(provider=provider, register=register)
        # check token len
        self.assertTrue(TOKEN_MAX_LEN >= len(token) > 0)
        self.assertTrue(macaroon_token.verify(token))
        caveats = extract_caveats(token)
        self.assertEqual(provider, caveats['provider'])
        self.assertEqual(register, caveats['register'])

    def test_token_root(self):
        user_root = User('root@hystax.com', self.type_root, 'pass',
                         display_name='I\'m root!', scope_id=None)
        self._check_token(user_root)

    def test_token_partner(self):
        user_partner = User('partner@hystax.com', self.type_partner, 'pass',
                            display_name='Partner user',
                            scope_id=str(uuid.uuid4()))
        self._check_token(user_partner)

    def test_token_customer(self):
        user_customer = User('customer@hystax.com', self.type_customer, 'pass',
                             display_name='Customer user',
                             scope_id=str(uuid.uuid4()))
        self._check_token(user_customer)

    def test_token_group(self):
        user_group = User('group@hystax.com', self.type_group, 'pass',
                          display_name='Group user', scope_id=str(uuid.uuid4()))
        self._check_token(user_group)

    def test_invalid_token(self):
        session = self.db_session
        fake_token = 'dpozskidKLklskldKLKL090ilokdlakodkads'
        user = User('customer@hystax.com', self.type_customer, 'pass',
                    display_name='Customer user', scope_id=str(uuid.uuid4()))
        session.add(user)
        session.commit()
        macaroon_token = MacaroonToken(user.salt, user.id)
        self.assertFalse(macaroon_token.verify(fake_token))

    def test_token_forgery(self):
        session = self.db_session
        user = User('customer@hystax.com', self.type_customer, 'pass',
                    display_name='Customer user', scope_id=str(uuid.uuid4()))
        session.add(user)
        session.commit()
        macaroon_token = MacaroonToken(user.salt, user.id)
        token = macaroon_token.create(True, 'google')
        macaroon_token._secret = 'fake'
        self.assertFalse(macaroon_token.verify(token))
