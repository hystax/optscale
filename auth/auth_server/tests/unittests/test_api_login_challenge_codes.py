import uuid
from datetime import timedelta
from unittest.mock import patch

import pyotp
import requests
from freezegun import freeze_time
from pymacaroons import Macaroon

from auth.auth_server.controllers.login_challenge import (
    LoginChallengeController)
from auth.auth_server.controllers.verification_code import (
    VerificationCodeController)
from auth.auth_server.models.models import (
    Assignment, AuthPolicy, AuthPolicyPurpose, AuthPolicyScope,
    LoginChallenge, MFAMethod, MFAType, Role, Type)
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import encrypt_mfa_secret
from tools.optscale_time import utcnow, utcnow_timestamp

HERALD_CLIENT = ('auth.auth_server.controllers.verification_code.'
                 'HeraldClient')
CONFIG_CLIENT = 'optscale_client.config_client.client.Client'
PRODUCT_NAME = 'FinOps for Cloud'
PASSWORD = 'toor'


class TestLoginChallengeCodes(TestAuthBase):
    """POST /login_challenge_codes: e-mail code during the MFA step
    (MPT-26347)"""

    def setUp(self, version='v2'):
        super().setUp(version)
        self.cluster_secret = self.client.secret
        self._start_patch(f'{CONFIG_CLIENT}.product_name',
                          return_value=PRODUCT_NAME)
        self._start_patch(f'{CONFIG_CLIENT}.herald_url',
                          return_value='http://herald')
        self.herald = self._start_patch(HERALD_CLIENT).return_value
        self.user = self.create_root_user(email='user@example.com',
                                          password=PASSWORD)
        self.other = self.create_root_user(email='other@example.com',
                                           password=PASSWORD)
        self.client.secret = None

    # --- helpers ---

    def _start_patch(self, target, **kwargs):
        """Started patches are stopped when the test ends: they must not
        leak into the other tests of the worker"""
        patcher = patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def _add_method(self, user=None, type_=MFAType.email, is_default=True,
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

    def _login(self, email='user@example.com'):
        code, resp = self.client.post(self.client.token_url(),
                                      {'email': email, 'password': PASSWORD})
        self.assertEqual(code, 202)
        return resp

    def _send(self, challenge_id, body=None):
        # the challenge id is the credential: in the body, not in the URL
        data = {'challenge_id': challenge_id}
        data.update(body or {})
        return self.client.post(self.client.login_challenge_codes_url(),
                                data)

    def _complete(self, challenge_id, code, method_id=None):
        body = {'challenge_id': challenge_id, 'code': code}
        if method_id is not None:
            body['method_id'] = method_id
        return self.client.post(self.client.token_url(), body)

    def _sent_code(self, call_idx=-1):
        kwargs = self.herald.email_send.call_args_list[call_idx].kwargs
        return kwargs['template_params']['texts']['code']

    def _challenge(self, challenge_id):
        self.db_session.expire_all()
        return self.db_session.query(LoginChallenge).get(challenge_id)

    @staticmethod
    def _mfa_caveat(token):
        caveats = [c.caveat_id for c in
                   Macaroon.deserialize(token).first_party_caveats()]
        return [c for c in caveats if c.startswith('mfa:')]

    def _enforce(self, user=None):
        session = self.db_session
        type_org = Type(id_=10, name='organization',
                        parent=self.create_root_type())
        role = Role(name='Member', type_=type_org, lvl=type_org,
                    description='member')
        org_id = str(uuid.uuid4())
        session.add_all([type_org, role,
                         Assignment(user or self.user, role, type_org,
                                    org_id),
                         AuthPolicy(scope_type=AuthPolicyScope.organization,
                                    scope_id=org_id,
                                    purpose=AuthPolicyPurpose.mfa)])
        session.commit()

    # --- happy paths ---

    def test_resend_default_email(self):
        email, _ = self._add_method()
        now = utcnow()
        with freeze_time(now):
            resp = self._login()
        self.assertTrue(resp['code_sent'])
        first_code = self._sent_code()
        # the code was just sent with the challenge: throttled
        with freeze_time(now + timedelta(seconds=30)):
            code, err = self._send(resp['challenge_id'],
                                   {'method_id': email.id})
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['error_code'], 'OA0072')
        self.assertEqual(self.herald.email_send.call_count, 1)
        with freeze_time(now + timedelta(seconds=61)):
            code, _ = self._send(resp['challenge_id'],
                                 {'method_id': email.id})
            self.assertEqual(code, 204)
            self.assertEqual(self.herald.email_send.call_count, 2)
            args, kwargs = self.herald.email_send.call_args
            self.assertEqual(args, (['user@example.com'],
                                    f'{PRODUCT_NAME}: your sign-in code'))
            self.assertEqual(kwargs['template_type'], 'mfa_login_code')
            second_code = self._sent_code()
            self.assertNotEqual(first_code, second_code)
            # the previous code is invalidated, the new one works
            code, err = self._complete(resp['challenge_id'], first_code)
            self.assertEqual(code, 403)
            self.assertEqual(err['error']['error_code'], 'OA0086')
            code, token = self._complete(resp['challenge_id'], second_code)
        self.assertEqual(code, 201)
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:email'])

    def test_send_for_non_default_email(self):
        # totp is the default: no code with the challenge, the user switches
        # to e-mail and asks for the code
        self._add_method(type_=MFAType.totp)
        email, _ = self._add_method(is_default=False)
        resp = self._login()
        self.assertFalse(resp['code_sent'])
        self.herald.email_send.assert_not_called()
        code, _ = self._send(resp['challenge_id'], {'method_id': email.id})
        self.assertEqual(code, 204)
        self.herald.email_send.assert_called_once()
        code, token = self._complete(resp['challenge_id'], self._sent_code(),
                                     email.id)
        self.assertEqual(code, 201)
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:email'])

    def test_method_id_optional(self):
        self._add_method(type_=MFAType.totp)
        self._add_method(is_default=False)
        resp = self._login()
        code, _ = self._send(resp['challenge_id'])
        self.assertEqual(code, 204)
        self.herald.email_send.assert_called_once()
        # completing without method_id: the default (totp) is tried first,
        # then... an e-mail code must name its method
        code, token = self._complete(resp['challenge_id'], self._sent_code())
        self.assertEqual(code, 403)

    def test_send_is_not_an_attempt(self):
        self._add_method(type_=MFAType.totp)
        self._add_method(is_default=False)
        resp = self._login()
        self._send(resp['challenge_id'])
        self.assertEqual(self._challenge(resp['challenge_id']).attempts, 0)
        code, err = self._complete(resp['challenge_id'], '000000')
        self.assertEqual(code, 403)
        self.assertEqual(err['error']['params'], [4])

    def test_send_with_token_header_ignored(self):
        # the challenge is the credential, a stale token does not matter
        self._add_method(type_=MFAType.totp)
        self._add_method(is_default=False)
        resp = self._login()
        self.client.token = 'not-a-token'
        code, _ = self._send(resp['challenge_id'])
        self.assertEqual(code, 204)

    # --- method validation (400) ---

    def test_totp_method_rejected(self):
        totp, _ = self._add_method(type_=MFAType.totp)
        self._add_method(is_default=False)
        resp = self._login()
        code, err = self._send(resp['challenge_id'], {'method_id': totp.id})
        self.assertEqual(code, 400)
        self.assertEqual(err['error']['error_code'], 'OA0060')
        self.herald.email_send.assert_not_called()

    def test_pending_email_rejected(self):
        self._add_method(type_=MFAType.totp)
        pending, _ = self._add_method(is_default=False, confirmed=False)
        resp = self._login()
        code, err = self._send(resp['challenge_id'],
                               {'method_id': pending.id})
        self.assertEqual(code, 400)
        self.assertEqual(err['error']['error_code'], 'OA0060')
        code, err = self._send(resp['challenge_id'])
        self.assertEqual(code, 400)
        self.assertEqual(err['error']['error_code'], 'OA0060')
        self.herald.email_send.assert_not_called()

    def test_foreign_email_rejected(self):
        self._add_method(type_=MFAType.totp)
        foreign, _ = self._add_method(user=self.other)
        resp = self._login()
        code, err = self._send(resp['challenge_id'],
                               {'method_id': foreign.id})
        self.assertEqual(code, 400)
        self.assertEqual(err['error']['error_code'], 'OA0060')
        self.herald.email_send.assert_not_called()

    def test_unknown_method_rejected(self):
        self._add_method()
        resp = self._login()
        code, err = self._send(resp['challenge_id'],
                               {'method_id': str(uuid.uuid4())})
        self.assertEqual(code, 400)
        self.assertEqual(err['error']['error_code'], 'OA0060')

    def test_removed_email_rejected(self):
        self._add_method(type_=MFAType.totp)
        email, _ = self._add_method(is_default=False)
        resp = self._login()
        email.deleted_at = utcnow_timestamp()
        self.db_session.commit()
        code, err = self._send(resp['challenge_id'], {'method_id': email.id})
        self.assertEqual(code, 400)
        self.assertEqual(err['error']['error_code'], 'OA0060')

    def test_no_email_method(self):
        self._add_method(type_=MFAType.totp)
        resp = self._login()
        code, err = self._send(resp['challenge_id'])
        self.assertEqual(code, 400)
        self.assertEqual(err['error']['error_code'], 'OA0060')

    def test_body_validation(self):
        self._add_method()
        resp = self._login()
        for body, error_code in [
            ({'method_id': 1}, 'OA0033'),
            ({'code': '123456'}, 'OA0022'),
            ({'method_id': None, 'email': 'x'}, 'OA0022'),
            # names of the arguments of the controller / of run_task: a 400
            # like any other unexpected key, not a TypeError (500)
            ({'func': 'x'}, 'OA0022'),
            ({'args': [], 'kwargs': {}}, 'OA0022'),
        ]:
            code, err = self._send(resp['challenge_id'], body)
            self.assertEqual(code, 400, body)
            self.assertEqual(err['error']['error_code'], error_code, body)
        url = self.client.login_challenge_codes_url()
        for body, error_code in [
            (['method_id'], 'OA0050'),
            ({}, 'OA0050'),
            ({'method_id': 'x'}, 'OA0032'),
            ({'challenge_id': None}, 'OA0032'),
            ({'challenge_id': 1}, 'OA0033'),
        ]:
            code, err = self.client.post(url, body)
            self.assertEqual(code, 400, body)
            self.assertEqual(err['error']['error_code'], error_code, body)
        # the code of the challenge was the only one sent
        self.assertEqual(self.herald.email_send.call_count, 1)

    # --- challenge validation (404) ---

    def test_enrollment_challenge_rejected(self):
        self._enforce()
        resp = self._login()
        self.assertEqual(resp['state'], 'enrollment_required')
        code, err = self._send(resp['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')
        self.herald.email_send.assert_not_called()

    def test_unknown_challenge(self):
        self._add_method()
        code, err = self._send(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_expired_challenge(self):
        self._add_method()
        now = utcnow()
        with freeze_time(now):
            resp = self._login()
        with freeze_time(now + timedelta(minutes=6)):
            code, err = self._send(resp['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')
        self.assertEqual(self.herald.email_send.call_count, 1)

    def test_completed_challenge(self):
        self._add_method()
        resp = self._login()
        code, _ = self._complete(resp['challenge_id'], self._sent_code())
        self.assertEqual(code, 201)
        code, err = self._send(resp['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_locked_challenge(self):
        self._add_method()
        resp = self._login()
        for _ in range(5):
            self._complete(resp['challenge_id'], '000000')
        code, err = self._send(resp['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_deactivated_user(self):
        self._add_method()
        resp = self._login()
        self.user.is_active = False
        self.db_session.commit()
        code, err = self._send(resp['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')

    def test_challenge_completed_before_lock(self):
        # a concurrent login completes (and reset_attempts removes) the
        # challenge between the checks and the user lock: the challenge is
        # read again under the lock, no e-mail is sent, 404 (not a 500 on a
        # row that is gone)
        self._add_method(type_=MFAType.totp)
        self._add_method(is_default=False)
        resp = self._login()
        lock_user = LoginChallengeController.lock_user

        def lock_then_remove(controller, user_id):
            lock_user(controller, user_id)
            controller.session.query(LoginChallenge).filter(
                LoginChallenge.id == resp['challenge_id']
            ).delete(synchronize_session=False)

        with patch.object(LoginChallengeController, 'lock_user',
                          lock_then_remove):
            code, err = self._send(resp['challenge_id'])
        self.assertEqual(code, 404)
        self.assertEqual(err['error']['error_code'], 'OA0085')
        self.herald.email_send.assert_not_called()

    def test_sent_under_user_lock(self):
        # the throttle check and the new code are serialized per user with
        # the lock, so concurrent requests cannot both pass the check
        self._add_method(type_=MFAType.totp)
        self._add_method(is_default=False)
        resp = self._login()
        calls = []
        lock_user = LoginChallengeController.lock_user

        def lock(controller, user_id):
            calls.append(('lock', user_id))
            lock_user(controller, user_id)

        def send(controller, user, purpose):
            calls.append(('send', user.id))

        with patch.object(LoginChallengeController, 'lock_user', lock), \
                patch.object(VerificationCodeController, 'send_mfa_code',
                             send):
            code, _ = self._send(resp['challenge_id'])
        self.assertEqual(code, 204)
        self.assertEqual(calls, [('lock', self.user.id),
                                 ('send', self.user.id)])

    # --- delivery ---

    def test_herald_down(self):
        self._add_method(type_=MFAType.totp)
        self._add_method(is_default=False)
        resp = self._login()
        self.herald.email_send.side_effect = (
            requests.exceptions.ConnectionError())
        code, _ = self._send(resp['challenge_id'])
        self.assertEqual(code, 503)
        # the undelivered code was dropped: a retry is not throttled
        self.herald.email_send.side_effect = None
        code, _ = self._send(resp['challenge_id'])
        self.assertEqual(code, 204)
