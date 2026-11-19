import logging
from datetime import timedelta
from unittest.mock import MagicMock, patch

import requests
import tornado.web
from freezegun import freeze_time

from tools.optscale_exceptions.common_exc import ForbiddenException
from tools.optscale_time import utcnow
from auth.auth_server.controllers.verification_code import (
    MfaCodePurpose, VerificationCodeController)
from auth.auth_server.models.models import (VerificationCode,
                                            VerificationCodePurpose)
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import get_digest

HERALD_CLIENT = ('auth.auth_server.controllers.verification_code.'
                 'HeraldClient')
LOGGER = 'auth.auth_server.controllers.verification_code'


class TestMfaCode(TestAuthBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        self.password = 'toor'
        self.user = self.create_root_user(password=self.password)
        self.config = MagicMock()
        self.config.herald_url.return_value = 'http://herald'
        self.config.cluster_secret.return_value = 'secret'
        self.config.product_name.return_value = 'FinOps for Cloud'
        self.herald_cls = patch(HERALD_CLIENT).start()
        self.herald = self.herald_cls.return_value

    @property
    def controller(self):
        return VerificationCodeController(self.db_session, self.config)

    def _sent_code(self, call_idx=-1):
        kwargs = self.herald.email_send.call_args_list[call_idx].kwargs
        return kwargs['template_params']['texts']['code']

    def _codes(self, purpose=None):
        query = self.db_session.query(VerificationCode).filter(
            VerificationCode.email == self.user.email)
        if purpose:
            query = query.filter(VerificationCode.purpose == purpose)
        return query.all()

    def _create_password_code(self, code):
        return self.controller.create_verification_code(
            self.user.email, code)

    def _send(self, purpose=MfaCodePurpose.login):
        return self.controller.send_mfa_code(self.user, purpose)

    def test_send_mfa_code(self):
        now = utcnow().replace(microsecond=0)
        with freeze_time(now):
            result = self.controller.send_mfa_code(
                self.user, MfaCodePurpose.enrollment)
        self.herald_cls.assert_called_once_with(url='http://herald',
                                                secret='secret')
        self.herald.email_send.assert_called_once()
        args, kwargs = self.herald.email_send.call_args
        # the subject and the template say what the code is for
        self.assertEqual(args, ([self.user.email],
                                'FinOps for Cloud: confirm your e-mail as '
                                'authentication method'))
        self.assertEqual(kwargs['template_type'], 'mfa_enrollment_code')
        code = self._sent_code()
        self.assertRegex(code, r'^\d{6}$')
        self.assertEqual(result.code, get_digest(code))
        self.assertEqual(result.purpose, VerificationCodePurpose.mfa)
        self.assertEqual(result.valid_until, now + timedelta(minutes=10))

    def test_send_login_code(self):
        self.controller.send_mfa_code(self.user, MfaCodePurpose.login)
        args, kwargs = self.herald.email_send.call_args
        self.assertEqual(args, ([self.user.email],
                                'FinOps for Cloud: your sign-in code'))
        self.assertEqual(kwargs['template_type'], 'mfa_login_code')
        # same code store and lifetime whatever the purpose of the e-mail
        self.assertEqual(self._codes(VerificationCodePurpose.mfa)[0].code,
                         get_digest(self._sent_code()))

    def test_send_unknown_purpose(self):
        with self.assertRaises(ValueError):
            self.controller.send_mfa_code(self.user, 'reset')
        self.herald.email_send.assert_not_called()
        self.assertEqual(self._codes(), [])

    def test_password_code_lifetime(self):
        now = utcnow().replace(microsecond=0)
        with freeze_time(now):
            result = self._create_password_code('123456')
        self.assertEqual(result.purpose, VerificationCodePurpose.password)
        self.assertEqual(result.valid_until, now + timedelta(hours=1))

    def test_mfa_code_lifetime(self):
        now = utcnow()
        with freeze_time(now):
            self._send()
        code = self._sent_code()
        with freeze_time(now + timedelta(minutes=10, seconds=1)):
            self.assertFalse(self.controller.use_verification_code(
                self.user.email, code, VerificationCodePurpose.mfa))
        with freeze_time(now + timedelta(minutes=9, seconds=59)):
            self.assertTrue(self.controller.use_verification_code(
                self.user.email, code, VerificationCodePurpose.mfa))

    def test_password_code_lifetime_usage(self):
        now = utcnow()
        with freeze_time(now):
            self._create_password_code('123456')
        with freeze_time(now + timedelta(minutes=59)):
            self.assertTrue(self.controller.use_verification_code(
                self.user.email, '123456'))

    def test_mfa_code_rejected_as_password_code(self):
        self._send()
        code = self._sent_code()
        self.assertFalse(self.controller.use_verification_code(
            self.user.email, code))
        self.assertFalse(self.controller.use_verification_code(
            self.user.email, code, VerificationCodePurpose.password))
        self.assertTrue(self.controller.use_verification_code(
            self.user.email, code, VerificationCodePurpose.mfa))

    def test_password_code_rejected_for_mfa(self):
        self._create_password_code('123456')
        self.assertFalse(self.controller.use_verification_code(
            self.user.email, '123456', VerificationCodePurpose.mfa))
        self.assertTrue(self.controller.use_verification_code(
            self.user.email, '123456'))

    def test_mfa_code_cannot_obtain_token(self):
        self._send()
        code = self._sent_code()
        self.client.secret = None
        code_, resp = self.client.post('tokens', {
            'email': self.user.email, 'verification_code': code})
        self.assertEqual(code_, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0071')

    def test_generation_threshold(self):
        now = utcnow()
        with freeze_time(now):
            self._send()
        first = self._codes(VerificationCodePurpose.mfa)[0]
        with freeze_time(now + timedelta(seconds=59)):
            with self.assertRaises(ForbiddenException) as ctx:
                self._send()
            self.assertEqual(ctx.exception.error_code, 'OA0072')
        self.assertEqual(self.herald.email_send.call_count, 1)
        with freeze_time(now + timedelta(minutes=1, seconds=1)):
            second = self._send()
        self.assertEqual(self.herald.email_send.call_count, 2)
        self.db_session.refresh(first)
        self.assertNotEqual(first.deleted_at, 0)
        self.assertEqual(second.deleted_at, 0)
        # the first code no longer works, the second one does
        with freeze_time(now + timedelta(minutes=1, seconds=2)):
            self.assertFalse(self.controller.use_verification_code(
                self.user.email, self._sent_code(0),
                VerificationCodePurpose.mfa))
            self.assertTrue(self.controller.use_verification_code(
                self.user.email, self._sent_code(1),
                VerificationCodePurpose.mfa))

    def test_purposes_are_independent(self):
        now = utcnow()
        with freeze_time(now):
            password_code = self._create_password_code('123456')
            # a fresh password code neither throttles nor invalidates MFA
            mfa_code = self._send()
        self.db_session.refresh(password_code)
        self.assertEqual(password_code.deleted_at, 0)
        with freeze_time(now + timedelta(minutes=1, seconds=1)):
            # a new password code invalidates only the previous password code
            code, _ = self.client.verification_code_create(
                self.user.email, '654321')
        self.assertEqual(code, 201)
        self.db_session.refresh(mfa_code)
        self.db_session.refresh(password_code)
        self.assertEqual(mfa_code.deleted_at, 0)
        self.assertNotEqual(password_code.deleted_at, 0)

    def test_mfa_code_does_not_throttle_password_code(self):
        now = utcnow()
        with freeze_time(now):
            self._send()
        with freeze_time(now + timedelta(seconds=10)):
            code, _ = self.client.verification_code_create(
                self.user.email, '123456')
        self.assertEqual(code, 201)

    def test_herald_failure(self):
        self.herald.email_send.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=500))
        with self.assertLogs(LOGGER, level=logging.INFO) as logs:
            with self.assertRaises(tornado.web.HTTPError) as ctx:
                self._send()
        self.assertEqual(ctx.exception.status_code, 503)
        code = self._sent_code()
        self.assertFalse(any(code in line for line in logs.output))
        # undelivered code is dropped, a new one can be requested at once
        self.assertEqual(self._codes(VerificationCodePurpose.mfa), [])
        self.herald.email_send.side_effect = None
        self._send()
        self.assertEqual(len(self._codes(VerificationCodePurpose.mfa)), 1)

    def test_herald_connection_error(self):
        self.herald.email_send.side_effect = (
            requests.exceptions.ConnectionError())
        with self.assertRaises(tornado.web.HTTPError) as ctx:
            self._send()
        self.assertEqual(ctx.exception.status_code, 503)

    def test_code_never_logged(self):
        with self.assertLogs(level=logging.DEBUG) as logs:
            self._send()
        code = self._sent_code()
        self.assertFalse(any(code in line for line in logs.output))

    def test_api_create_rejects_purpose(self):
        code, resp = self.client.post('verification_codes', {
            'email': self.user.email, 'code': '123456', 'purpose': 'mfa'})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0022')
        self.assertEqual(self._codes(), [])

    def test_api_create_password_purpose(self):
        code, resp = self.client.verification_code_create(
            self.user.email, '123456')
        self.assertEqual(code, 201)
        self.assertEqual(resp['purpose'], 'password')
