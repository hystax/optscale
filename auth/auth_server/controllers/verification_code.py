import logging
import secrets
from datetime import timedelta
from enum import Enum
from functools import cached_property

import requests
import tornado.web
from sqlalchemy import and_, exists
from sqlalchemy.exc import IntegrityError
from auth.auth_server.controllers.base import BaseController
from auth.auth_server.models.models import (VerificationCode,
                                            VerificationCodePurpose)
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import User
from auth.auth_server.utils import get_digest
from optscale_client.herald_client.client_v2 import Client as HeraldClient
from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  ForbiddenException)
from tools.optscale_time import utcnow

LOG = logging.getLogger(__name__)
VERIFICATION_CODE_LIFETIME_HRS = 1
MFA_CODE_LIFETIME_MIN = 10
GENERATION_THRESHOLD_MIN = 1
MFA_CODE_LENGTH = 6


class MfaCodePurpose(Enum):
    """Why an MFA code is sent: the e-mail must say what the code is for"""
    enrollment = 'enrollment'
    login = 'login'


# herald template and subject (after the product name) per purpose
MFA_CODE_EMAILS = {
    MfaCodePurpose.enrollment: (
        'mfa_enrollment_code',
        'confirm your e-mail as authentication method'),
    MfaCodePurpose.login: ('mfa_login_code', 'your sign-in code'),
}


def get_code_lifetime(purpose):
    if VerificationCodePurpose(purpose) == VerificationCodePurpose.mfa:
        return timedelta(minutes=MFA_CODE_LIFETIME_MIN)
    return timedelta(hours=VERIFICATION_CODE_LIFETIME_HRS)


def generate_code():
    return f'{secrets.randbelow(10 ** MFA_CODE_LENGTH):0{MFA_CODE_LENGTH}d}'


class VerificationCodeController(BaseController):
    def _get_model_type(self):
        return VerificationCode

    def _check_user(self, email):
        user = self.session.query(User).filter(
            and_(
                User.email == email,
                User.deleted.is_(False)
            )
        ).one_or_none()
        if not user:
            raise WrongArgumentsException(Err.OA0037, [])
        return user

    def _check_input(self, **input_):
        email = input_.get('email')
        if not email:
            raise WrongArgumentsException(Err.OA0032, ['email'])
        verification_code = input_.get('code')
        if not verification_code:
            raise WrongArgumentsException(Err.OA0032, ['code'])
        self._check_generation_timeout(email)
        return self._check_user(email)

    def _check_generation_timeout(
            self, email, purpose=VerificationCodePurpose.password):
        model = self._get_model_type()
        timeout = utcnow() - timedelta(
            minutes=GENERATION_THRESHOLD_MIN)
        code_exists = self.session.query(exists().where(and_(
            model.email == email,
            model.purpose == VerificationCodePurpose(purpose),
            model.created_at >= int(timeout.timestamp())
        ))).scalar()
        if code_exists:
            raise ForbiddenException(Err.OA0072, [])

    def create(self, **kwargs):
        # the public (cluster secret) endpoint only issues recovery codes,
        # MFA codes are generated and sent by auth itself (send_mfa_code)
        if 'purpose' in kwargs:
            raise WrongArgumentsException(Err.OA0022, ['purpose'])
        self.check_create_restrictions(**kwargs)
        self._check_input(**kwargs)
        return self.create_verification_code(**kwargs)

    def _invalidate_verification_codes(
            self, email, deleted_at,
            purpose=VerificationCodePurpose.password):
        model = self._get_model_type()
        self.session.query(model).filter(
            model.email == email,
            model.purpose == VerificationCodePurpose(purpose),
            model.deleted.is_(False)
        ).update({
            model.deleted_at: deleted_at
        })

    def create_verification_code(self, email, code,
                                 purpose=VerificationCodePurpose.password):
        model_type = self._get_model_type()
        purpose = VerificationCodePurpose(purpose)
        LOG.info("Creating %s (%s) for %s", model_type.__name__,
                 purpose.value, email)
        now = utcnow()
        now_ts = int(now.timestamp())
        params = {
            'email': email,
            'created_at': now_ts,
            'valid_until': now + get_code_lifetime(purpose),
            'code': get_digest(str(code)),
            'purpose': purpose,
        }
        verification_code = model_type(**params)
        self._invalidate_verification_codes(email, now_ts, purpose)
        self.session.add(verification_code)
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OA0061, [str(ex)])
        return verification_code

    @cached_property
    def herald_client(self):
        return HeraldClient(url=self._config.herald_url(),
                            secret=self._config.cluster_secret())

    def send_mfa_code(self, user, purpose):
        """
        Generates an MFA code for the user, stores its digest (purpose mfa,
        previous MFA codes invalidated) and sends it by e-mail via herald,
        with the template and subject of the given MfaCodePurpose
        (enrollment of the e-mail method or sign-in).
        Raises ForbiddenException (OA0072) if a code was generated less than
        a minute ago and HTTPError 503 if herald is unavailable.
        The code itself is never logged.
        """
        template, subject = MFA_CODE_EMAILS[MfaCodePurpose(purpose)]
        self._check_generation_timeout(user.email,
                                       VerificationCodePurpose.mfa)
        code = generate_code()
        verification_code = self.create_verification_code(
            user.email, code, VerificationCodePurpose.mfa)
        try:
            self.herald_client.email_send(
                [user.email],
                f'{self._config.product_name()}: {subject}',
                template_type=template,
                template_params={'texts': {'code': code}})
        except requests.exceptions.RequestException as exc:
            LOG.error('Failed to send MFA code to user %s: %s',
                      user.id, type(exc).__name__)
            # drop the undelivered code so the user can request a new one
            # without waiting for the generation threshold
            self.session.delete(verification_code)
            self.session.commit()
            raise tornado.web.HTTPError(503, reason='Service Unavailable')
        LOG.info('MFA code sent to user %s', user.id)
        return verification_code


class VerificationCodeAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return VerificationCodeController
