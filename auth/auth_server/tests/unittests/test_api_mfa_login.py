import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pyotp
import requests
from freezegun import freeze_time
from pymacaroons import Macaroon

from auth.auth_server.controllers.auth_policy import AuthPolicyController
from auth.auth_server.controllers.login_challenge import (
    LoginChallengeController)
from auth.auth_server.controllers.mfa_method import MfaMethodController
from auth.auth_server.controllers.verification_code import (
    VerificationCodeController)
from auth.auth_server.models.models import (
    User, Token, Assignment, AuthPolicy, AuthPolicyPurpose, AuthPolicyScope,
    LoginChallenge, MFAMethod, MFAType, Role, Type)
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import encrypt_mfa_secret
from tools.optscale_exceptions.common_exc import NotFoundException
from tools.optscale_time import utcnow, utcnow_timestamp

HERALD_CLIENT = ('auth.auth_server.controllers.verification_code.'
                 'HeraldClient')
CONFIG_CLIENT = 'optscale_client.config_client.client.Client'
PRODUCT_NAME = 'FinOps for Cloud'
PASSWORD = 'toor'
TOKEN_KEYS = {'token', 'user_id', 'user_email', 'created_at', 'valid_until',
              'ip', 'digest'}


class TestMfaLogin(TestAuthBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        self.cluster_secret = self.client.secret
        patch(f'{CONFIG_CLIENT}.product_name',
              return_value=PRODUCT_NAME).start()
        patch(f'{CONFIG_CLIENT}.herald_url',
              return_value='http://herald').start()
        self.herald = patch(HERALD_CLIENT).start().return_value
        self.user = self.create_root_user(email='user@example.com',
                                          password=PASSWORD)
        self.other = self.create_root_user(email='other@example.com',
                                           password=PASSWORD)
        self.client.secret = None
        self.org_id = str(uuid.uuid4())

    # --- helpers ---

    def _add_method(self, user=None, type_=MFAType.totp, is_default=True,
                    confirmed=True):
        seed = pyotp.random_base32() if type_ == MFAType.totp else None
        method = MFAMethod(
            user_id=(user or self.user).id, type=type_,
            secret=encrypt_mfa_secret(seed) if seed else None,
            label='label', is_default=is_default)
        if confirmed:
            method.confirmed_at = utcnow_timestamp()
        self.db_session.add(method)
        self.db_session.commit()
        return method, seed

    def _enforce(self, user=None):
        session = self.db_session
        type_org = session.query(Type).filter_by(name='organization').first()
        if type_org is None:
            type_org = Type(id_=10, name='organization',
                            parent=self.create_root_type())
            session.add(type_org)
        role = Role(name='Member', type_=type_org, lvl=type_org,
                    description='member')
        session.add(role)
        session.add(Assignment(user or self.user, role, type_org,
                               self.org_id))
        session.add(AuthPolicy(scope_type=AuthPolicyScope.organization,
                               scope_id=self.org_id,
                               purpose=AuthPolicyPurpose.mfa))
        session.commit()

    def _login(self, email='user@example.com', **body):
        body = body or {'password': PASSWORD}
        return self.client.post(self.client.token_url(),
                                {'email': email, **body})

    def _complete(self, challenge_id, code, method_id=None):
        body = {'challenge_id': challenge_id, 'code': code}
        if method_id is not None:
            body['method_id'] = method_id
        return self.client.post(self.client.token_url(), body)

    def _challenge(self, challenge_id):
        self.db_session.expire_all()
        return self.db_session.query(LoginChallenge).get(challenge_id)

    def _sent_code(self):
        kwargs = self.herald.email_send.call_args.kwargs
        return kwargs['template_params']['texts']['code']

    @staticmethod
    def _mfa_caveat(token):
        caveats = [c.caveat_id for c in
                   Macaroon.deserialize(token).first_party_caveats()]
        return [c for c in caveats if c.startswith('mfa:')]

    @staticmethod
    def _wrong(code):
        return f'{(int(code) + 1) % 1_000_000:06d}'

    # --- no MFA ---

    def test_password_only_unchanged(self):
        code, resp = self._login()
        self.assertEqual(code, 201)
        self.assertEqual(set(resp), TOKEN_KEYS)
        self.assertEqual(resp['user_email'], 'user@example.com')
        self.assertEqual(self._mfa_caveat(resp['token']), ['mfa:none'])
        self.assertEqual(self.db_session.query(LoginChallenge).count(), 0)

    def test_pending_method_only(self):
        self._add_method(confirmed=False)
        code, _ = self._login()
        self.assertEqual(code, 201)

    def test_cluster_secret_user_id_untouched(self):
        self._add_method()
        self._enforce()
        self.client.secret = self.cluster_secret
        code, resp = self.client.token_get_user_id(self.user.id)
        self.assertEqual(code, 201)
        self.assertIn('token', resp)

    def test_wrong_password_no_challenge(self):
        self._add_method()
        code, resp = self._login(password='wrong')
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0037')
        self.assertEqual(self.db_session.query(LoginChallenge).count(), 0)

    # --- mfa_required ---

    def test_totp_challenge(self):
        method, seed = self._add_method()
        now = utcnow_timestamp()
        code, resp = self._login()
        self.assertEqual(code, 202)
        self.assertEqual(resp['state'], 'mfa_required')
        self.assertEqual(resp['user_email'], 'user@example.com')
        self.assertEqual(resp['default_method_id'], method.id)
        self.assertFalse(resp['code_sent'])
        self.assertEqual(resp['attempts_left'], 5)
        self.assertAlmostEqual(resp['expires_at'], now + 300, delta=2)
        self.assertEqual(resp['methods'], [{
            'id': method.id, 'type': 'totp', 'label': 'label',
            'is_default': True, 'confirmed': True}])
        self.assertNotIn('token', resp)
        self.herald.email_send.assert_not_called()

        code, token = self._complete(resp['challenge_id'],
                                     pyotp.TOTP(seed).now(), method.id)
        self.assertEqual(code, 201)
        self.assertEqual(set(token), TOKEN_KEYS)
        self.assertEqual(token['user_id'], self.user.id)
        self.assertEqual(token['user_email'], 'user@example.com')
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:totp'])
        # used: removed with the attempts reset
        self.assertIsNone(self._challenge(resp['challenge_id']))
        # the token works
        self.client.token = token['token']
        code, _ = self.client.user_get(self.user.id)
        self.assertEqual(code, 200)

    def test_default_method_when_no_method_id(self):
        _, seed = self._add_method()
        _, resp = self._login()
        code, token = self._complete(resp['challenge_id'],
                                     pyotp.TOTP(seed).now())
        self.assertEqual(code, 201)
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:totp'])

    def test_challenge_single_use(self):
        _, seed = self._add_method()
        _, resp = self._login()
        self._complete(resp['challenge_id'], pyotp.TOTP(seed).now())
        code, err = self._complete(resp['challenge_id'],
                                   pyotp.TOTP(seed).now())
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_totp_code_not_reusable_in_new_challenge(self):
        _, seed = self._add_method()
        totp_code = pyotp.TOTP(seed).now()
        _, first = self._login()
        self._complete(first['challenge_id'], totp_code)
        _, second = self._login()
        code, err = self._complete(second['challenge_id'], totp_code)
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0086')

    def test_email_default_code_sent(self):
        self._add_method(type_=MFAType.email)
        code, resp = self._login()
        self.assertEqual(code, 202)
        self.assertTrue(resp['code_sent'])
        self.herald.email_send.assert_called_once()
        self.assertEqual(self.herald.email_send.call_args.kwargs[
            'template_type'], 'mfa_code')
        code, token = self._complete(resp['challenge_id'], self._sent_code())
        self.assertEqual(code, 201)
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:email'])

    def test_email_not_default_no_code_sent(self):
        self._add_method()
        email, _ = self._add_method(type_=MFAType.email, is_default=False)
        code, resp = self._login()
        self.assertEqual(code, 202)
        self.assertFalse(resp['code_sent'])
        self.herald.email_send.assert_not_called()
        self.assertEqual(len(resp['methods']), 2)
        # the default method comes first
        self.assertTrue(resp['methods'][0]['is_default'])
        # the user picks email: code requested separately (MPT-26347)
        config = MagicMock()
        config.product_name.return_value = PRODUCT_NAME
        VerificationCodeController(self.db_session, config).send_mfa_code(
            self.user)
        code, token = self._complete(resp['challenge_id'], self._sent_code(),
                                     email.id)
        self.assertEqual(code, 201)
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:email'])

    def test_email_herald_down_login_continues(self):
        self._add_method(type_=MFAType.email)
        self.herald.email_send.side_effect = (
            requests.exceptions.ConnectionError())
        code, resp = self._login()
        self.assertEqual(code, 202)
        self.assertFalse(resp['code_sent'])

    def test_email_throttled_login_continues(self):
        self._add_method(type_=MFAType.email)
        now = utcnow()
        with freeze_time(now):
            self._login()
        with freeze_time(now + timedelta(seconds=30)):
            code, resp = self._login()
        self.assertEqual(code, 202)
        self.assertFalse(resp['code_sent'])
        self.assertEqual(self.herald.email_send.call_count, 1)

    def test_unknown_method_id(self):
        _, seed = self._add_method()
        pending, _ = self._add_method(type_=MFAType.email, is_default=False,
                                      confirmed=False)
        foreign, _ = self._add_method(user=self.other)
        _, resp = self._login()
        for method_id in [str(uuid.uuid4()), pending.id, foreign.id]:
            code, err = self._complete(resp['challenge_id'],
                                       pyotp.TOTP(seed).now(), method_id)
            self.assertEqual(code, 404, method_id)
            self.assertEqual(err['error']['error_code'], 'OA0003')
        # no attempts used
        self.assertEqual(self._challenge(resp['challenge_id']).attempts, 0)

    def test_wrong_code_attempts_left(self):
        _, seed = self._add_method()
        _, resp = self._login()
        wrong = self._wrong(pyotp.TOTP(seed).now())
        code, err = self._complete(resp['challenge_id'], wrong)
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0086')
        self.assertEqual(err['error']['params'], [4])
        self.assertIn('4 attempts left', err['error']['reason'])
        # still usable with the right code
        code, _ = self._complete(resp['challenge_id'],
                                 pyotp.TOTP(seed).now())
        self.assertEqual(code, 201)

    def test_locked_after_five_failures(self):
        _, seed = self._add_method()
        _, resp = self._login()
        wrong = self._wrong(pyotp.TOTP(seed).now())
        for left in [4, 3, 2, 1]:
            code, err = self._complete(resp['challenge_id'], wrong)
            self.assertEqual(err['error']['params'], [left])
        code, err = self._complete(resp['challenge_id'], wrong)
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0087')
        self.assertTrue(self._challenge(resp['challenge_id']).deleted)
        # even the right code no longer works
        code, err = self._complete(resp['challenge_id'],
                                   pyotp.TOTP(seed).now())
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')
        # a new sign in starts over
        code, _ = self._login()
        self.assertEqual(code, 202)

    def test_expired_challenge(self):
        _, seed = self._add_method()
        now = utcnow()
        with freeze_time(now):
            _, resp = self._login()
        with freeze_time(now + timedelta(minutes=5, seconds=1)):
            code, err = self._complete(resp['challenge_id'],
                                       pyotp.TOTP(seed).now())
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_expired_challenges_cleaned_on_new_login(self):
        self._add_method()
        now = utcnow()
        with freeze_time(now):
            _, first = self._login()
        # expired, but kept for the user's attempts window
        with freeze_time(now + timedelta(minutes=6)):
            _, second = self._login()
        self.assertIsNotNone(self._challenge(first['challenge_id']))
        # window (15) + lifetime (5)
        with freeze_time(now + timedelta(minutes=15, seconds=1)):
            self._login()
        self.assertIsNotNone(self._challenge(first['challenge_id']))
        with freeze_time(now + timedelta(minutes=20, seconds=1)):
            _, third = self._login()
        self.assertIsNone(self._challenge(first['challenge_id']))
        self.assertIsNotNone(self._challenge(second['challenge_id']))
        self.assertIsNotNone(self._challenge(third['challenge_id']))

    # --- attempts budget of the user (all challenges) ---

    def _fail(self, challenge_id, times, seed):
        wrong = self._wrong(pyotp.TOTP(seed).now())
        for _ in range(times):
            code, err = self._complete(challenge_id, wrong)
            self.assertEqual(code, 403)
        return err

    def test_new_login_does_not_reset_attempts(self):
        _, seed = self._add_method()
        _, first = self._login()
        err = self._fail(first['challenge_id'], 5, seed)
        self.assertEqual(err['error']['error_code'], 'OA0087')
        _, second = self._login()
        err = self._fail(second['challenge_id'], 5, seed)
        # 10 attempts of the user used: the 5th of the second challenge
        # was still checked (OA0087), no more attempts now
        self.assertEqual(err['error']['error_code'], 'OA0087')
        code, err = self._login()
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0090')
        self.herald.email_send.assert_not_called()

    def test_attempts_budget_checked_on_each_attempt(self):
        _, seed = self._add_method()
        _, first = self._login()
        _, second = self._login()
        self._fail(first['challenge_id'], 4, seed)
        self._fail(second['challenge_id'], 4, seed)
        _, third = self._login()
        self._fail(third['challenge_id'], 2, seed)
        # 10 attempts used: even the right code is refused
        code, err = self._complete(third['challenge_id'],
                                   pyotp.TOTP(seed).now())
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0090')
        self.assertEqual(self._challenge(third['challenge_id']).attempts, 2)

    def test_attempts_budget_window(self):
        _, seed = self._add_method()
        now = utcnow()
        with freeze_time(now):
            for _ in range(2):
                _, challenge = self._login()
                self._fail(challenge['challenge_id'], 5, seed)
            code, err = self._login()
            self.assertEqual(code, 403)
            self.assertEqual(err['error']['error_code'], 'OA0090')
        with freeze_time(now + timedelta(minutes=20, seconds=1)):
            code, challenge = self._login()
            self.assertEqual(code, 202)
            # pyotp now() is local time, wrong with a frozen naive time
            code, resp = self._complete(
                challenge['challenge_id'],
                pyotp.TOTP(seed).at(utcnow_timestamp()))
            self.assertEqual(code, 201, resp)

    def test_attempts_counted_from_last_guess(self):
        # guesses made at the end of the challenges lifetime still count
        # 15 minutes later
        _, seed = self._add_method()
        now = utcnow()
        with freeze_time(now):
            _, first = self._login()
            _, second = self._login()
        with freeze_time(now + timedelta(minutes=4, seconds=59)):
            self._fail(first['challenge_id'], 5, seed)
            self._fail(second['challenge_id'], 5, seed)
        with freeze_time(now + timedelta(minutes=15, seconds=1)):
            code, err = self._login()
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0090')
        with freeze_time(now + timedelta(minutes=20, seconds=1)):
            code, _ = self._login()
        self.assertEqual(code, 202)

    def test_success_resets_attempts(self):
        _, seed = self._add_method()
        _, first = self._login()
        self._fail(first['challenge_id'], 5, seed)
        _, second = self._login()
        self._fail(second['challenge_id'], 4, seed)
        code, _ = self._complete(second['challenge_id'],
                                 pyotp.TOTP(seed).now())
        self.assertEqual(code, 201)
        self.assertEqual(self.db_session.query(LoginChallenge).count(), 0)
        _, third = self._login()
        err = self._fail(third['challenge_id'], 1, seed)
        self.assertEqual(err['error']['error_code'], 'OA0086')
        self.assertEqual(err['error']['params'], [4])

    def test_success_keeps_other_open_challenges(self):
        method, seed = self._add_method()
        _, first = self._login()
        _, second = self._login()
        self._fail(second['challenge_id'], 1, seed)
        code, resp = self._complete(first['challenge_id'],
                                    pyotp.TOTP(seed).now())
        self.assertEqual(code, 201, resp)
        self.assertIsNone(self._challenge(first['challenge_id']))
        # another sign in still open: kept with its attempts
        self.assertEqual(self._challenge(second['challenge_id']).attempts, 1)

    def test_enrollment_attempts_count_for_user(self):
        self._enforce()
        _, first = self._login()
        _, method = self._enroll(first['challenge_id'])
        wrong = self._wrong(pyotp.TOTP(method['secret']).now())
        for _ in range(5):
            self._confirm(method['id'], wrong, first['challenge_id'])
        _, second = self._login()
        for _ in range(5):
            self._confirm(method['id'], wrong, second['challenge_id'])
        code, err = self._login()
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0090')

    def test_challenge_id_not_logged(self):
        _, seed = self._add_method()
        with self.assertLogs('auth.auth_server.controllers',
                             level='INFO') as logs:
            _, challenge = self._login()
            self._fail(challenge['challenge_id'], 1, seed)
            self._complete(challenge['challenge_id'], pyotp.TOTP(seed).now())
        output = '\n'.join(logs.output)
        self.assertIn('Login challenge completed', output)
        self.assertNotIn(challenge['challenge_id'], output)

    def test_enrollment_challenge_id_not_logged(self):
        self._enforce()
        with self.assertLogs('auth.auth_server.controllers',
                             level='INFO') as logs:
            _, challenge = self._login()
            _, method = self._enroll(challenge['challenge_id'])
            self._confirm(
                method['id'], self._wrong(pyotp.TOTP(method['secret']).now()),
                challenge['challenge_id'])
            self._confirm(method['id'], pyotp.TOTP(method['secret']).now(),
                          challenge['challenge_id'])
        output = '\n'.join(logs.output)
        self.assertIn('completed for user', output)
        self.assertNotIn(challenge['challenge_id'], output)

    def test_unknown_challenge(self):
        code, err = self._complete(str(uuid.uuid4()), '123456')
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_inactive_user_challenge(self):
        _, seed = self._add_method()
        _, resp = self._login()
        self.user.is_active = False
        self.db_session.commit()
        code, err = self._complete(resp['challenge_id'],
                                   pyotp.TOTP(seed).now())
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_complete_validation(self):
        self._add_method()
        _, resp = self._login()
        url = self.client.token_url()
        for body, error_code in [
            ({'challenge_id': resp['challenge_id']}, 'OA0032'),
            ({'challenge_id': resp['challenge_id'], 'code': 123456},
             'OA0033'),
            ({'challenge_id': resp['challenge_id'], 'code': '123456',
              'method_id': 1}, 'OA0033'),
            ({'challenge_id': 1, 'code': '123456'}, 'OA0033'),
            ({'challenge_id': resp['challenge_id'], 'code': '123456',
              'foo': 'bar'}, 'OA0022'),
        ]:
            code, err = self.client.post(url, body)
            self.assertEqual(code, 400, body)
            self.assertEqual(err['error']['error_code'], error_code, body)

    def test_verification_code_login_goes_through_mfa(self):
        _, seed = self._add_method()
        self.client.secret = self.cluster_secret
        self.client.verification_code_create(self.user.email, '123456')
        self.client.secret = None
        code, resp = self._login(verification_code='123456')
        self.assertEqual(code, 202)
        self.assertEqual(resp['state'], 'mfa_required')
        code, token = self._complete(resp['challenge_id'],
                                     pyotp.TOTP(seed).now())
        self.assertEqual(code, 201)

    # --- enrollment_required ---

    def test_enforced_without_method(self):
        self._enforce()
        code, resp = self._login()
        self.assertEqual(code, 202)
        self.assertEqual(resp['state'], 'enrollment_required')
        # needed to build the enrollment URL, the client has no token
        self.assertEqual(resp['user_id'], self.user.id)
        self.assertEqual(resp['methods'], [])
        self.assertIsNone(resp['default_method_id'])
        self.assertFalse(resp['code_sent'])
        # nothing to complete with a code: enroll first
        code, err = self._complete(resp['challenge_id'], '123456')
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0088')

    def test_enforced_with_method(self):
        self._add_method()
        self._enforce()
        code, resp = self._login()
        self.assertEqual(code, 202)
        self.assertEqual(resp['state'], 'mfa_required')

    def test_enforcement_of_other_user_only(self):
        self._enforce(user=self.other)
        code, _ = self._login()
        self.assertEqual(code, 201)

    def _enroll(self, challenge_id, type_='totp', user_id=None):
        return self.client.post(
            self.client.mfa_methods_url(user_id or self.user.id),
            {'type': type_, 'challenge_id': challenge_id})

    def _confirm(self, method_id, code, challenge_id, user_id=None):
        return self.client.post(
            self.client.mfa_method_confirm_url(user_id or self.user.id,
                                               method_id),
            {'code': code, 'challenge_id': challenge_id})

    def test_enroll_with_challenge(self):
        self._enforce()
        _, challenge = self._login()
        code, method = self._enroll(challenge['challenge_id'])
        self.assertEqual(code, 201)
        seed = method['secret']
        code, resp = self._confirm(method['id'], pyotp.TOTP(seed).now(),
                                   challenge['challenge_id'])
        self.assertEqual(code, 201)
        self.assertEqual(resp['method']['id'], method['id'])
        self.assertTrue(resp['method']['confirmed'])
        self.assertTrue(resp['method']['is_default'])
        self.assertNotIn('secret', resp['method'])
        token = resp['token']
        self.assertEqual(set(token), TOKEN_KEYS)
        self.assertEqual(token['user_email'], 'user@example.com')
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:totp'])
        self.assertIsNone(self._challenge(challenge['challenge_id']))
        # the next sign in asks for the code
        code, resp = self._login()
        self.assertEqual(code, 202)
        self.assertEqual(resp['state'], 'mfa_required')

    def test_enroll_email_with_challenge(self):
        self._enforce()
        _, challenge = self._login()
        _, method = self._enroll(challenge['challenge_id'], 'email')
        code, resp = self._confirm(method['id'], self._sent_code(),
                                   challenge['challenge_id'])
        self.assertEqual(code, 201)
        self.assertEqual(self._mfa_caveat(resp['token']['token']),
                         ['mfa:email'])

    def test_enroll_challenge_wrong_code(self):
        self._enforce()
        _, challenge = self._login()
        _, method = self._enroll(challenge['challenge_id'])
        code, err = self._confirm(
            method['id'], self._wrong(pyotp.TOTP(method['secret']).now()),
            challenge['challenge_id'])
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0086')
        self.assertEqual(err['error']['params'], [4])
        challenge_db = self._challenge(challenge['challenge_id'])
        self.assertFalse(challenge_db.deleted)
        self.assertEqual(challenge_db.attempts, 1)

    def test_enroll_challenge_locked_after_five_failures(self):
        self._enforce()
        _, challenge = self._login()
        _, method = self._enroll(challenge['challenge_id'])
        wrong = self._wrong(pyotp.TOTP(method['secret']).now())
        for attempts_left in [4, 3, 2, 1]:
            code, err = self._confirm(method['id'], wrong,
                                      challenge['challenge_id'])
            self.assertEqual(code, 403)
            self.assertEqual(err['error']['error_code'], 'OA0086')
            self.assertEqual(err['error']['params'], [attempts_left])
        code, err = self._confirm(method['id'], wrong,
                                  challenge['challenge_id'])
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0087')
        self.assertTrue(self._challenge(challenge['challenge_id']).deleted)
        # even the right code is rejected now: sign in again
        code, err = self._confirm(method['id'],
                                  pyotp.TOTP(method['secret']).now(),
                                  challenge['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')
        self.db_session.expire_all()
        self.assertFalse(self.db_session.query(MFAMethod).get(
            method['id']).confirmed)

    def test_enroll_other_challenge_after_first_method(self):
        self._enforce()
        _, first = self._login()
        _, second = self._login()
        _, method = self._enroll(first['challenge_id'], 'email')
        code, _ = self._confirm(method['id'], self._sent_code(),
                                first['challenge_id'])
        self.assertEqual(code, 201)
        # the second challenge cannot add a method skipping the email one
        # (invalidated, then removed with the attempts reset)
        self.assertIsNone(self._challenge(second['challenge_id']))
        code, err = self._enroll(second['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_enroll_challenge_with_confirmed_method(self):
        # a method confirmed while the challenge is open (e.g. with a
        # token), the challenge cannot enroll anymore
        self._enforce()
        _, challenge = self._login()
        self._add_method(type_=MFAType.email)
        code, err = self._enroll(challenge['challenge_id'])
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0089')

    def test_confirm_challenge_with_confirmed_method(self):
        # two pending enrollments of different challenges: only the first
        # confirmation is accepted
        self._enforce()
        _, first = self._login()
        _, second = self._login()
        _, totp = self._enroll(first['challenge_id'])
        _, email = self._enroll(second['challenge_id'], 'email')
        code, _ = self._confirm(email['id'], self._sent_code(),
                                second['challenge_id'])
        self.assertEqual(code, 201)
        code, err = self._confirm(totp['id'],
                                  pyotp.TOTP(totp['secret']).now(),
                                  first['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')
        self.db_session.expire_all()
        self.assertFalse(self.db_session.query(MFAMethod).get(
            totp['id']).confirmed)

    def test_confirm_with_token_wrong_code_no_attempts(self):
        self.client.secret = self.cluster_secret
        _, method = self.client.post(self.client.mfa_methods_url(
            self.user.id), {'type': 'totp'})
        wrong = self._wrong(pyotp.TOTP(method['secret']).now())
        for _ in range(6):
            code, err = self.client.post(
                self.client.mfa_method_confirm_url(self.user.id,
                                                   method['id']),
                {'code': wrong})
            self.assertEqual(code, 403)
            self.assertEqual(err['error']['error_code'], 'OA0083')

    def _change_password(self, password='NewPassword1!'):
        self.client.secret = self.cluster_secret
        _, token = self.client.token_get_user_id(self.user.id)
        self.client.secret = None
        self.client.token = token['token']
        code, _ = self.client.user_update(self.user.id, password=password)
        self.assertEqual(code, 200)
        self.client.token = None

    def test_password_change_invalidates_challenges(self):
        method, seed = self._add_method()
        _, mfa_challenge = self._login()
        self._change_password()
        self.assertTrue(self._challenge(mfa_challenge['challenge_id']).deleted)
        code, err = self._complete(mfa_challenge['challenge_id'],
                                   pyotp.TOTP(seed).now(), method.id)
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_password_change_invalidates_enrollment_challenges(self):
        self._enforce()
        _, challenge = self._login()
        self._change_password()
        code, err = self._enroll(challenge['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_other_edit_keeps_challenges(self):
        self._add_method()
        _, challenge = self._login()
        self.client.secret = self.cluster_secret
        _, token = self.client.token_get_user_id(self.user.id)
        self.client.secret = None
        self.client.token = token['token']
        code, _ = self.client.user_update(self.user.id, display_name='new')
        self.assertEqual(code, 200)
        self.assertFalse(self._challenge(challenge['challenge_id']).deleted)

    def test_enroll_challenge_single_use(self):
        self._enforce()
        _, challenge = self._login()
        _, method = self._enroll(challenge['challenge_id'])
        self._confirm(method['id'], pyotp.TOTP(method['secret']).now(),
                      challenge['challenge_id'])
        code, err = self._enroll(challenge['challenge_id'], 'email')
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_enroll_challenge_of_other_user(self):
        self._enforce()
        _, challenge = self._login()
        code, err = self._enroll(challenge['challenge_id'],
                                 user_id=self.other.id)
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0012')

    def test_enroll_with_mfa_required_challenge_forbidden(self):
        self._add_method(type_=MFAType.email)
        _, challenge = self._login()
        # the password alone must not allow adding a method
        code, err = self._enroll(challenge['challenge_id'])
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0012')

    def test_enroll_expired_challenge(self):
        self._enforce()
        now = utcnow()
        with freeze_time(now):
            _, challenge = self._login()
        with freeze_time(now + timedelta(minutes=5, seconds=1)):
            code, err = self._enroll(challenge['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_confirm_without_challenge_still_200(self):
        self._enforce()
        self.client.secret = self.cluster_secret
        _, method = self.client.post(self.client.mfa_methods_url(
            self.user.id), {'type': 'totp'})
        code, resp = self.client.post(
            self.client.mfa_method_confirm_url(self.user.id, method['id']),
            {'code': pyotp.TOTP(method['secret']).now()})
        self.assertEqual(code, 200)
        self.assertNotIn('token', resp)

    # --- concurrency: state changed by another request meanwhile ---

    def _challenges(self):
        return LoginChallengeController(self.db_session, MagicMock())

    def _delete_challenge(self, challenge_id):
        self.db_session.query(LoginChallenge).filter(
            LoginChallenge.id == challenge_id).delete()
        self.db_session.commit()

    def test_consume_expired_challenge(self):
        # expired between get_valid and consume
        self._add_method()
        now = utcnow()
        with freeze_time(now):
            _, challenge = self._login()
        with freeze_time(now + timedelta(minutes=5, seconds=1)):
            with self.assertRaises(NotFoundException) as ctx:
                self._challenges().consume(challenge['challenge_id'])
        self.assertEqual(ctx.exception.error_code, 'OA0085')
        self.assertFalse(self._challenge(challenge['challenge_id']).deleted)

    def test_attempt_on_expired_challenge(self):
        self._add_method()
        now = utcnow()
        with freeze_time(now):
            _, challenge = self._login()
        with freeze_time(now + timedelta(minutes=5, seconds=1)):
            with self.assertRaises(NotFoundException) as ctx:
                self._challenges().register_attempt(
                    challenge['challenge_id'], self.user.id)
        self.assertEqual(ctx.exception.error_code, 'OA0085')
        self.assertEqual(self._challenge(challenge['challenge_id']).attempts,
                         0)

    def test_removed_challenge_no_500(self):
        # removed by a concurrent completion (attempts reset)
        self._add_method()
        _, challenge = self._login()
        for call in [lambda c: c.register_attempt(challenge['challenge_id'],
                                                  self.user.id),
                     lambda c: c.consume(challenge['challenge_id'])]:
            self._delete_challenge(challenge['challenge_id'])
            with self.assertRaises(NotFoundException) as ctx:
                call(self._challenges())
            self.assertEqual(ctx.exception.error_code, 'OA0085')

    def test_challenge_removed_during_verification(self):
        _, seed = self._add_method()
        _, challenge = self._login()

        def verify(*_args):
            self._delete_challenge(challenge['challenge_id'])
            return True
        with patch.object(MfaMethodController, 'verify_code',
                          side_effect=verify):
            code, err = self._complete(challenge['challenge_id'],
                                       pyotp.TOTP(seed).now())
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def _change_salt(self):
        self.db_session.query(User).filter(User.id == self.user.id).update(
            {User.salt: 'changed'})
        self.db_session.commit()

    def _before_sign_in_lock(self, action):
        """runs action after the password check, before the user lock
        (the window where concurrent requests can still commit)"""
        original = LoginChallengeController.lock_sign_in

        def lock(controller, user_id, salt):
            action()
            return original(controller, user_id, salt)
        return patch.object(LoginChallengeController, 'lock_sign_in',
                            autospec=True, side_effect=lock)

    def _check_password_changed_during_sign_in(self):
        tokens = self.db_session.query(Token).count()
        with self._before_sign_in_lock(self._change_salt):
            code, err = self._login()
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0037')
        self.assertEqual(self.db_session.query(LoginChallenge).count(), 0)
        self.assertEqual(self.db_session.query(Token).count(), tokens)

    def test_password_changed_before_challenge_created(self):
        self._enforce()
        self._check_password_changed_during_sign_in()

    def test_password_changed_before_mfa_challenge_created(self):
        self._add_method()
        self._check_password_changed_during_sign_in()

    def test_password_changed_before_token_created(self):
        # no MFA: the password-only token is protected as well
        self._check_password_changed_during_sign_in()

    def test_method_confirmed_during_sign_in(self):
        # the first method is confirmed (e.g. from another session) after
        # the password check: no password-only token
        with self._before_sign_in_lock(lambda: self._add_method()):
            code, resp = self._login()
        self.assertEqual(code, 202)
        self.assertEqual(resp['state'], 'mfa_required')
        self.assertNotIn('token', resp)

    def test_enforcement_during_sign_in(self):
        with self._before_sign_in_lock(self._enforce):
            code, resp = self._login()
        self.assertEqual(code, 202)
        self.assertEqual(resp['state'], 'enrollment_required')

    def test_token_signed_with_salt_at_completion(self):
        # the user is read again under the lock: the token is signed with
        # the salt current when the challenge is consumed
        _, seed = self._add_method()
        _, challenge = self._login()
        code, resp = self._complete(challenge['challenge_id'],
                                    pyotp.TOTP(seed).now())
        self.assertEqual(code, 201)
        self.client.token = resp['token']
        code, _ = self.client.user_get(self.user.id)
        self.assertEqual(code, 200)
        self._change_salt()
        code, _ = self.client.user_get(self.user.id)
        self.assertEqual(code, 401)

    def _confirm_meanwhile(self, first_challenge_id):
        """send_mfa_code side effect: another challenge confirms the
        pending email method while the new enrollment sends its e-mail"""
        def send(controller, user):
            method = self.db_session.query(MFAMethod).filter(
                MFAMethod.user_id == user.id,
                MFAMethod.type == MFAType.email).one()
            method.confirmed_at = utcnow_timestamp()
            method.is_default = True
            self.db_session.query(LoginChallenge).filter(
                LoginChallenge.id != first_challenge_id).update(
                {LoginChallenge.deleted_at: utcnow_timestamp()})
            self.db_session.commit()
        return send

    def test_enrollment_does_not_remove_confirmed_method(self):
        self._enforce()
        _, first = self._login()
        _, second = self._login()
        _, method = self._enroll(first['challenge_id'], 'email')
        with patch.object(VerificationCodeController, 'send_mfa_code',
                          autospec=True,
                          side_effect=self._confirm_meanwhile(
                              first['challenge_id'])):
            code, err = self._enroll(second['challenge_id'], 'email')
        # the second challenge was revoked by the confirmation
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')
        self.db_session.expire_all()
        confirmed = self.db_session.query(MFAMethod).get(method['id'])
        self.assertTrue(confirmed.confirmed)
        self.assertFalse(confirmed.deleted)

    def test_enrollment_with_token_does_not_remove_confirmed_method(self):
        self.client.secret = self.cluster_secret
        _, method = self.client.post(self.client.mfa_methods_url(
            self.user.id), {'type': 'email'})
        with patch.object(VerificationCodeController, 'send_mfa_code',
                          autospec=True,
                          side_effect=self._confirm_meanwhile(None)):
            code, err = self.client.post(self.client.mfa_methods_url(
                self.user.id), {'type': 'email'})
        self.assertEqual(code, 409)
        self.assertEqual(err['error']['error_code'], 'OA0082')
        self.db_session.expire_all()
        self.assertTrue(self.db_session.query(MFAMethod).get(
            method['id']).confirmed)

    def test_confirm_replaced_enrollment(self):
        # the pending method is replaced by a new enrollment while its code
        # is checked
        self._enforce()
        _, challenge = self._login()
        _, method = self._enroll(challenge['challenge_id'])
        original = MfaMethodController.verify_code

        def verify(controller, method_, code_):
            result = original(controller, method_, code_)
            self.db_session.query(MFAMethod).filter(
                MFAMethod.id == method['id']).delete()
            self.db_session.commit()
            return result
        with patch.object(MfaMethodController, 'verify_code',
                          autospec=True, side_effect=verify):
            code, err = self._confirm(method['id'],
                                      pyotp.TOTP(method['secret']).now(),
                                      challenge['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0003')
        # not used: the user can still enroll
        self.assertFalse(self._challenge(challenge['challenge_id']).deleted)

    def _deactivate_during_verify(self, field, value):
        original = MfaMethodController.verify_code

        def verify(controller, method_, code_):
            result = original(controller, method_, code_)
            self.db_session.query(User).filter(
                User.id == self.user.id).update({field: value})
            self.db_session.commit()
            return result
        return patch.object(MfaMethodController, 'verify_code',
                            autospec=True, side_effect=verify)

    def _tokens_count(self):
        self.db_session.expire_all()
        return self.db_session.query(Token).filter(
            Token.user_id == self.user.id).count()

    def _check_login_user_changed(self, field, value):
        _, seed = self._add_method()
        _, challenge = self._login()
        tokens = self._tokens_count()
        with self._deactivate_during_verify(field, value):
            code, err = self._complete(challenge['challenge_id'],
                                       pyotp.TOTP(seed).now())
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')
        self.assertEqual(self._tokens_count(), tokens)
        # rolled back: not consumed
        self.assertFalse(self._challenge(challenge['challenge_id']).deleted)

    def test_user_deactivated_during_login(self):
        self._check_login_user_changed(User.is_active, False)

    def test_user_deleted_during_login(self):
        self._check_login_user_changed(User.deleted_at, utcnow_timestamp())

    def test_user_deactivated_during_enrollment(self):
        self._enforce()
        _, challenge = self._login()
        _, method = self._enroll(challenge['challenge_id'])
        tokens = self._tokens_count()
        with self._deactivate_during_verify(User.is_active, False):
            code, err = self._confirm(method['id'],
                                      pyotp.TOTP(method['secret']).now(),
                                      challenge['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')
        self.assertEqual(self._tokens_count(), tokens)
        self.assertFalse(self.db_session.query(MFAMethod).get(
            method['id']).confirmed)

    def test_enrollment_replaced_before_verification(self):
        # removed after the attempt is registered, before the code check
        self._enforce()
        _, challenge = self._login()
        _, method = self._enroll(challenge['challenge_id'])
        original = LoginChallengeController.register_attempt

        def register(controller, challenge_id, user_id):
            result = original(controller, challenge_id, user_id)
            self.db_session.query(MFAMethod).filter(
                MFAMethod.id == method['id']).delete()
            self.db_session.commit()
            return result
        with patch.object(LoginChallengeController, 'register_attempt',
                          autospec=True, side_effect=register):
            code, err = self._confirm(method['id'],
                                      pyotp.TOTP(method['secret']).now(),
                                      challenge['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0003')
        self.assertFalse(self._challenge(challenge['challenge_id']).deleted)

    # --- codes with non-ASCII digits ---

    ARABIC_INDIC = '\u0661\u0662\u0663\u0664\u0665\u0666'

    def test_non_ascii_code_login(self):
        for type_ in [MFAType.totp, MFAType.email]:
            self.db_session.query(MFAMethod).delete()
            self.db_session.commit()
            self._add_method(type_=type_)
            _, challenge = self._login()
            code, err = self._complete(challenge['challenge_id'],
                                       self.ARABIC_INDIC)
            self.assertEqual(code, 403, type_)
            self.assertEqual(err['error']['error_code'], 'OA0086')
            self.assertEqual(err['error']['params'], [4])

    def test_non_ascii_code_enrollment_with_challenge(self):
        self._enforce()
        _, challenge = self._login()
        _, method = self._enroll(challenge['challenge_id'])
        code, err = self._confirm(method['id'], self.ARABIC_INDIC,
                                  challenge['challenge_id'])
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0086')

    def test_non_ascii_code_enrollment_with_token(self):
        self.client.secret = self.cluster_secret
        _, method = self.client.post(self.client.mfa_methods_url(
            self.user.id), {'type': 'totp'})
        code, err = self.client.post(
            self.client.mfa_method_confirm_url(self.user.id, method['id']),
            {'code': self.ARABIC_INDIC})
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0083')

    # --- pending method removed during the TOTP check ---

    def _remove_during_totp(self, method_id, before):
        original = MfaMethodController._verify_totp

        def remove():
            self.db_session.query(MFAMethod).filter(
                MFAMethod.id == method_id).delete()
            self.db_session.commit()

        def verify_totp(controller, method_, code_):
            if before:
                remove()
            result = original(controller, method_, code_)
            if not before:
                remove()
            return result
        return patch.object(MfaMethodController, '_verify_totp',
                            autospec=True, side_effect=verify_totp)

    def test_enrollment_removed_during_totp_check(self):
        self._enforce()
        for before in [True, False]:
            _, challenge = self._login()
            _, method = self._enroll(challenge['challenge_id'])
            with self._remove_during_totp(method['id'], before):
                code, err = self._confirm(method['id'],
                                          pyotp.TOTP(method['secret']).now(),
                                          challenge['challenge_id'])
            self.assertEqual(code, 404, before)
            self.assertEqual(err['error']['error_code'], 'OA0003')
            self.assertFalse(
                self._challenge(challenge['challenge_id']).deleted)

    def test_enrollment_with_token_removed_during_totp_check(self):
        self.client.secret = self.cluster_secret
        _, method = self.client.post(self.client.mfa_methods_url(
            self.user.id), {'type': 'totp'})
        with self._remove_during_totp(method['id'], before=False):
            code, err = self.client.post(
                self.client.mfa_method_confirm_url(self.user.id,
                                                   method['id']),
                {'code': pyotp.TOTP(method['secret']).now()})
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0003')

    def test_enrollment_with_token_second_method_not_default(self):
        self._add_method(type_=MFAType.email)
        self.client.secret = self.cluster_secret
        _, method = self.client.post(self.client.mfa_methods_url(
            self.user.id), {'type': 'totp'})
        code, resp = self.client.post(
            self.client.mfa_method_confirm_url(self.user.id, method['id']),
            {'code': pyotp.TOTP(method['secret']).now()})
        self.assertEqual(code, 200)
        self.assertTrue(resp['confirmed'])
        self.assertFalse(resp['is_default'])
