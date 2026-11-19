from datetime import timedelta, timezone
from unittest.mock import patch
from urllib.parse import parse_qs, unquote, urlparse

import pyotp
import requests
from freezegun import freeze_time

from auth.auth_server.controllers.mfa_method import MfaMethodController
from auth.auth_server.models.models import MFAMethod, MFAType, gen_salt
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import (
    build_otpauth_uri, decrypt_mfa_secret, encrypt_mfa_secret, mask_email)
from tools.optscale_time import utcnow, utcnow_timestamp

HERALD_CLIENT = ('auth.auth_server.controllers.verification_code.'
                 'HeraldClient')
CONFIG_CLIENT = 'optscale_client.config_client.client.Client'
ENCRYPTION_SALT = 'auth.auth_server.utils.get_encryption_salt'
PRODUCT_NAME = 'FinOps for Cloud'
PASSWORD = 'toor'


class TestMfaUtils(TestAuthBase):
    def test_secret_round_trip(self):
        seed = pyotp.random_base32()
        encrypted = encrypt_mfa_secret(seed)
        self.assertNotIn(seed, encrypted)
        self.assertLessEqual(len(encrypted), MFAMethod.secret.type.length)
        self.assertEqual(decrypt_mfa_secret(encrypted), seed)
        # random IV: the same seed never gives the same ciphertext
        self.assertNotEqual(encrypt_mfa_secret(seed), encrypted)

    def test_secret_needs_same_salt(self):
        encrypted = encrypt_mfa_secret(pyotp.random_base32())
        with patch(ENCRYPTION_SALT, return_value=gen_salt()):
            with self.assertRaises(ValueError):
                decrypt_mfa_secret(encrypted)

    def test_otpauth_uri(self):
        uri = build_otpauth_uri(PRODUCT_NAME, 'reto.mayer@example.com',
                                'JBSWY3DPEHPK3PXP')
        self.assertEqual(
            uri, 'otpauth://totp/FinOps%20for%20Cloud:reto.mayer%40'
                 'example.com?secret=JBSWY3DPEHPK3PXP&issuer=FinOps%20for'
                 '%20Cloud&digits=6&period=30')
        # pyotp reads back what an authenticator app would
        totp = pyotp.parse_uri(uri)
        self.assertEqual(totp.secret, 'JBSWY3DPEHPK3PXP')
        self.assertEqual(totp.issuer, PRODUCT_NAME)
        self.assertEqual(totp.name, 'reto.mayer@example.com')
        self.assertEqual(totp.digits, 6)
        self.assertEqual(totp.interval, 30)

    def test_mask_email(self):
        self.assertEqual(mask_email('finops.ffc@example.com'),
                         'fi***@example.com')
        self.assertEqual(mask_email('a@example.com'), 'a***@example.com')


class TestMfaMethods(TestAuthBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        self.cluster_secret = self.client.secret
        patch(f'{CONFIG_CLIENT}.product_name',
              return_value=PRODUCT_NAME).start()
        patch(f'{CONFIG_CLIENT}.herald_url',
              return_value='http://herald').start()
        self.herald = patch(HERALD_CLIENT).start().return_value
        self.user = self.create_root_user(email='owner@example.com',
                                          password=PASSWORD)
        self.other = self.create_root_user(email='other@example.com',
                                           password=PASSWORD)
        self._login(self.user)

    def _login(self, user):
        self.client.secret = self.cluster_secret
        self.client.token = self.get_token(user.email, PASSWORD)
        self.client.secret = None

    def _use_secret(self):
        self.client.token = None
        self.client.secret = self.cluster_secret

    def _enroll(self, type_='totp', user_id=None, **body):
        if type_ == 'totp':
            body.setdefault('label', 'Pixel 10 Pro')
        return self.client.post(
            self.client.mfa_methods_url(user_id or self.user.id),
            {'type': type_, **body})

    def _confirm(self, method_id, code, user_id=None):
        return self.client.post(self.client.mfa_method_confirm_url(
            user_id or self.user.id, method_id), {'code': code})

    def _method(self, method_id):
        self.db_session.expire_all()
        return self.db_session.query(MFAMethod).get(method_id)

    def _sent_code(self):
        kwargs = self.herald.email_send.call_args.kwargs
        return kwargs['template_params']['texts']['code']

    @property
    def controller(self):
        return MfaMethodController(self.db_session)

    @staticmethod
    def _totp_code(seed, timestamp=None):
        return pyotp.TOTP(seed).at(timestamp or utcnow_timestamp())

    @staticmethod
    def _wrong(code):
        return f'{(int(code) + 1) % 1_000_000:06d}'

    # --- totp enrollment ---

    def test_enroll_totp(self):
        code, resp = self._enroll(label='Pixel 10 Pro')
        self.assertEqual(code, 201)
        self.assertEqual(resp['type'], 'totp')
        self.assertEqual(resp['label'], 'Pixel 10 Pro')
        self.assertEqual(resp['user_id'], self.user.id)
        self.assertFalse(resp['confirmed'])
        self.assertFalse(resp['is_default'])
        self.assertNotIn('last_used_step', resp)
        seed = resp['secret']
        self.assertEqual(len(seed), 32)
        self.assertEqual(pyotp.parse_uri(resp['otpauth_uri']).secret, seed)
        self.assertIn(f'otpauth://totp/{PRODUCT_NAME}:owner@example.com',
                      unquote(resp['otpauth_uri']))
        # stored encrypted, never in clear
        method = self._method(resp['id'])
        self.assertNotEqual(method.secret, seed)
        self.assertEqual(decrypt_mfa_secret(method.secret), seed)
        self.herald.email_send.assert_not_called()

    def test_confirm_totp(self):
        _, method = self._enroll()
        code, resp = self._confirm(method['id'],
                                   self._totp_code(method['secret']))
        self.assertEqual(code, 200)
        self.assertTrue(resp['confirmed'])
        self.assertNotEqual(resp['confirmed_at'], 0)
        # first confirmed method becomes default
        self.assertTrue(resp['is_default'])
        self.assertNotIn('secret', resp)
        self.assertNotIn('otpauth_uri', resp)
        self.assertNotIn('last_used_step', resp)
        self.assertTrue(self._method(method['id']).confirmed)

    def test_confirm_totp_previous_step_accepted(self):
        _, method = self._enroll()
        code = self._totp_code(method['secret'], utcnow_timestamp() - 30)
        code_, _ = self._confirm(method['id'], code)
        self.assertEqual(code_, 200)

    def test_confirm_totp_old_code_rejected(self):
        _, method = self._enroll()
        code = self._totp_code(method['secret'], utcnow_timestamp() - 90)
        code_, resp = self._confirm(method['id'], code)
        self.assertEqual(code_, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0083')

    def test_confirm_wrong_code(self):
        _, method = self._enroll()
        wrong = self._wrong(self._totp_code(method['secret']))
        code, resp = self._confirm(method['id'], wrong)
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0083')
        method_db = self._method(method['id'])
        self.assertFalse(method_db.confirmed)
        self.assertEqual(method_db.last_used_step, 0)
        # still pending, the right code works afterwards
        code, _ = self._confirm(method['id'],
                                self._totp_code(method['secret']))
        self.assertEqual(code, 200)

    def test_confirm_malformed_codes(self):
        _, method = self._enroll()
        for bad in ['', '12345', '1234567', 'abcdef', ' 12345']:
            code, resp = self._confirm(method['id'], bad)
            self.assertEqual(code, 403, bad)
            self.assertEqual(resp['error']['error_code'], 'OA0083')

    def test_confirm_code_validation(self):
        _, method = self._enroll()
        url = self.client.mfa_method_confirm_url(self.user.id, method['id'])
        for body, error_code in [
            ({'code': None}, 'OA0032'),
            ({'code': 123456}, 'OA0033'),
            ({'code': '123456', 'extra': 1}, 'OA0022'),
        ]:
            code, resp = self.client.post(url, body)
            self.assertEqual(code, 400, body)
            self.assertEqual(resp['error']['error_code'], error_code)

    def test_confirm_twice(self):
        _, method = self._enroll()
        self._confirm(method['id'], self._totp_code(method['secret']))
        code, resp = self._confirm(method['id'],
                                   self._totp_code(method['secret']))
        self.assertEqual(code, 409)
        self.assertEqual(resp['error']['error_code'], 'OA0084')

    def test_totp_replay_rejected(self):
        _, method = self._enroll()
        totp_code = self._totp_code(method['secret'])
        self._confirm(method['id'], totp_code)
        method_db = self._method(method['id'])
        self.assertEqual(method_db.last_used_step,
                         utcnow_timestamp() // 30)
        # the code used to confirm can't be used again (e.g. at login)
        self.assertFalse(self.controller.verify_code(method_db, totp_code))

    def test_totp_older_step_rejected_after_newer_used(self):
        _, method = self._enroll()
        now = utcnow_timestamp()
        method_db = self._method(method['id'])
        self.assertTrue(self.controller.verify_code(
            method_db, self._totp_code(method['secret'], now)))
        # a code of the previous step is in the window but older than the
        # last accepted one
        self.assertFalse(self.controller.verify_code(
            method_db, self._totp_code(method['secret'], now - 30)))

    def test_verify_code_next_step(self):
        _, method = self._enroll()
        method_db = self._method(method['id'])
        now = utcnow_timestamp()
        self.assertTrue(self.controller.verify_code(
            method_db, self._totp_code(method['secret'], now + 30)))
        self.assertFalse(self.controller.verify_code(
            method_db, self._totp_code(method['secret'], now)))

    # --- duplicates and pending enrollments ---

    def test_duplicate_email_conflict(self):
        _, method = self._enroll('email')
        self._confirm(method['id'], self._sent_code())
        code, resp = self._enroll('email')
        self.assertEqual(code, 409)
        self.assertEqual(resp['error']['error_code'], 'OA0082')
        self.assertEqual(self.db_session.query(MFAMethod).count(), 1)

    def test_several_totp_methods(self):
        _, first = self._enroll(label='Phone')
        self._confirm(first['id'], self._totp_code(first['secret']))
        code, second = self._enroll(label='Tablet')
        self.assertEqual(code, 201)
        self.assertNotEqual(second['secret'], first['secret'])
        # the confirmed method is not touched by the new enrollment
        self.assertTrue(self._method(first['id']).confirmed)
        code, resp = self._confirm(second['id'],
                                   self._totp_code(second['secret']))
        self.assertEqual(code, 200)
        self.assertTrue(resp['confirmed'])
        self.assertFalse(resp['is_default'])
        self.assertEqual(resp['label'], 'Tablet')
        self.assertEqual(
            [m.label for m in self.controller.get_confirmed_methods(
                self.user.id)], ['Phone', 'Tablet'])

    def test_restart_pending_enrollment(self):
        _, first = self._enroll()
        code, second = self._enroll()
        self.assertEqual(code, 201)
        self.assertNotEqual(first['id'], second['id'])
        self.assertNotEqual(first['secret'], second['secret'])
        self.assertIsNone(self._method(first['id']))
        code, _ = self._confirm(first['id'],
                                self._totp_code(first['secret']))
        self.assertEqual(code, 404)
        code, _ = self._confirm(second['id'],
                                self._totp_code(second['secret']))
        self.assertEqual(code, 200)

    def test_expired_pending_enrollment(self):
        now = utcnow()
        with freeze_time(now):
            _, method = self._enroll()
        with freeze_time(now + timedelta(minutes=15, seconds=1)):
            code, resp = self._confirm(
                method['id'], self._totp_code(method['secret']))
            self.assertEqual(code, 404)
            self.assertEqual(resp['error']['error_code'], 'OA0003')
            # discarded on the next enrollment of any type
            code, _ = self._enroll('email')
            self.assertEqual(code, 201)
        self.assertIsNone(self._method(method['id']))

    def test_pending_within_lifetime(self):
        now = utcnow()
        with freeze_time(now):
            _, method = self._enroll()
        later = now + timedelta(minutes=14, seconds=59)
        with freeze_time(later):
            code, _ = self._confirm(method['id'], self._totp_code(
                method['secret'],
                int(later.replace(tzinfo=timezone.utc).timestamp())))
        self.assertEqual(code, 200)

    def test_second_method_not_default(self):
        _, totp = self._enroll()
        self._confirm(totp['id'], self._totp_code(totp['secret']))
        _, email = self._enroll('email')
        code, resp = self._confirm(email['id'], self._sent_code())
        self.assertEqual(code, 200)
        self.assertFalse(resp['is_default'])
        self.assertTrue(self._method(totp['id']).is_default)

    # --- email ---

    def test_enroll_email(self):
        code, resp = self._enroll('email', label='ignored')
        self.assertEqual(code, 201)
        self.assertEqual(resp['type'], 'email')
        self.assertEqual(resp['label'], 'ow***@example.com')
        self.assertNotIn('secret', resp)
        self.assertNotIn('otpauth_uri', resp)
        self.assertIsNone(self._method(resp['id']).secret)
        self.herald.email_send.assert_called_once()
        args, kwargs = self.herald.email_send.call_args
        # the enrollment e-mail, not the sign-in one
        self.assertEqual(args, (['owner@example.com'],
                                f'{PRODUCT_NAME}: confirm your e-mail as '
                                'authentication method'))
        self.assertEqual(kwargs['template_type'], 'mfa_enrollment_code')

    def test_confirm_email(self):
        _, method = self._enroll('email')
        code, resp = self._confirm(method['id'], self._sent_code())
        self.assertEqual(code, 200)
        self.assertTrue(resp['confirmed'])
        self.assertTrue(resp['is_default'])

    def test_confirm_email_wrong_code(self):
        _, method = self._enroll('email')
        code, resp = self._confirm(method['id'],
                                   self._wrong(self._sent_code()))
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0083')
        self.assertFalse(self._method(method['id']).confirmed)

    def test_email_code_used_once(self):
        _, method = self._enroll('email')
        sent = self._sent_code()
        self._confirm(method['id'], sent)
        self.assertFalse(self.controller.verify_code(
            self._method(method['id']), sent))

    def test_email_restart_throttled(self):
        now = utcnow()
        with freeze_time(now):
            _, first = self._enroll('email')
        with freeze_time(now + timedelta(seconds=30)):
            code, resp = self._enroll('email')
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0072')
        # the pending enrollment is kept and its code still works
        self.assertIsNotNone(self._method(first['id']))
        code, _ = self._confirm(first['id'], self._sent_code())
        self.assertEqual(code, 200)

    def test_email_herald_down(self):
        self.herald.email_send.side_effect = (
            requests.exceptions.ConnectionError())
        code, _ = self._enroll('email')
        self.assertEqual(code, 503)
        self.assertEqual(self.db_session.query(MFAMethod).count(), 0)

    # --- input validation ---

    def test_enroll_validation(self):
        for body, error_code in [
            ({'label': 'Pixel 10 Pro'}, 'OA0032'),
            # the label is required for totp (several apps), not for email
            ({'type': 'totp'}, 'OA0032'),
            ({'type': 1}, 'OA0033'),
            ({'type': 'sms'}, 'OA0060'),
            ({'type': 'totp', 'label': 'x' * 257}, 'OA0048'),
            ({'type': 'totp', 'label': '   '}, 'OA0065'),
            ({'type': 'totp', 'label': 1}, 'OA0033'),
            ({'type': 'totp', 'is_default': True}, 'OA0022'),
            ({'type': 'totp', 'secret': 'JBSWY3DPEHPK3PXP'}, 'OA0022'),
        ]:
            code, resp = self.client.post(
                self.client.mfa_methods_url(self.user.id), body)
            self.assertEqual(code, 400, body)
            self.assertEqual(resp['error']['error_code'], error_code, body)
        self.assertEqual(self.db_session.query(MFAMethod).count(), 0)

    # --- access ---

    def test_foreign_token_forbidden(self):
        code, resp = self._enroll(user_id=self.other.id)
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')
        self._login(self.other)
        _, method = self._enroll(user_id=self.other.id)
        self._login(self.user)
        code, resp = self._confirm(method['id'],
                                   self._totp_code(method['secret']),
                                   user_id=self.other.id)
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')
        self.assertFalse(self._method(method['id']).confirmed)

    def test_method_of_another_user_not_found(self):
        self._login(self.other)
        _, method = self._enroll(user_id=self.other.id)
        self._login(self.user)
        # the owner's own URL with someone else's method id
        code, resp = self._confirm(method['id'],
                                   self._totp_code(method['secret']))
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0003')

    def test_cluster_secret(self):
        self._use_secret()
        code, method = self._enroll()
        self.assertEqual(code, 201)
        code, _ = self._confirm(method['id'],
                                self._totp_code(method['secret']))
        self.assertEqual(code, 200)

    def test_unauthorized(self):
        self.client.token = None
        self.client.secret = None
        code, _ = self._enroll()
        self.assertEqual(code, 401)

    def test_unknown_user(self):
        self._use_secret()
        code, resp = self._enroll(user_id='unknown')
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0024')

    def test_list_returns_status(self):
        # GET is the MFA status (MPT-26345, test_api_mfa_management)
        code, resp = self.client.get(
            self.client.mfa_methods_url(self.user.id))
        self.assertEqual(code, 200)
        self.assertEqual(resp['status'], 'not_configured')

    def test_to_dict_never_exposes_secret(self):
        _, method = self._enroll()
        method_dict = self._method(method['id']).to_dict()
        self.assertNotIn('secret', method_dict)
        self.assertNotIn('last_used_step', method_dict)
        self.assertEqual(MFAType(method_dict['type']), MFAType.totp)
