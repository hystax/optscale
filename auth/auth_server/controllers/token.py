import logging
import tornado.web
from sqlalchemy import and_

from auth.auth_server.controllers.auth_policy import AuthPolicyController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.controllers.login_challenge import (
    LoginChallengeController)
from auth.auth_server.controllers.mfa_method import MfaMethodController
from auth.auth_server.controllers.token_issuer import TokenIssuer
from auth.auth_server.controllers.verification_code import (
    VerificationCodeController)
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import (
    LoginChallengeState, MFAType, User)
from auth.auth_server.utils import (hash_password, popkey,
                                    raise_not_provided_error)

from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  ForbiddenException,
                                                  NotFoundException)

LOG = logging.getLogger(__name__)


class TokenController(TokenIssuer):
    @property
    def create_restrictions(self):
        return super().create_restrictions + [
            'email', 'password', 'verification_code', 'challenge_id', 'code',
            'method_id']

    def _check_user(self, email, password=None, verification_code=None):
        user = self.session.query(User).filter(
            and_(
                User.email == email,
                User.deleted.is_(False)
            )
        ).one_or_none()
        if not user:
            raise ForbiddenException(
                Err.OA0037 if password else Err.OA0071, [])
        if password:
            if user.password != hash_password(password, user.salt):
                raise ForbiddenException(Err.OA0037, [])
            if not user.verified:
                raise ForbiddenException(Err.OA0073, [])
        else:
            vc_used = self.use_verification_code(email, verification_code)
            if not vc_used:
                raise ForbiddenException(Err.OA0071, [])
            elif not user.verified:
                user.verified = True
        if not user.is_active:
            raise ForbiddenException(Err.OA0038, [])
        return user

    def _check_input(self, **input_):
        email = input_.get('email')
        password = input_.get('password')
        verification_code = input_.get('verification_code')
        if not email or not (password or verification_code):
            raise WrongArgumentsException(Err.OA0039, [])
        user = self._check_user(email, password, verification_code)
        return user

    def create(self, **kwargs):
        """
        Returns a token, or a login challenge (dict with challenge_id) when
        a second factor is needed. Called again with challenge_id + code to
        complete the challenge.
        """
        if kwargs.get('challenge_id') is not None:
            return self._complete_challenge(**kwargs)
        user = self._check_input(**kwargs)
        user_id, salt = user.id, user.salt
        popkey(kwargs, 'password')
        popkey(kwargs, 'verification_code')
        # from here to the commit of the challenge or of the token under the
        # user lock: the MFA decision cannot miss a method confirmed (or a
        # password changed) meanwhile
        challenges = LoginChallengeController(self.session, self._config)
        challenges.lock_sign_in(user_id, salt)
        user = self.session.query(User).filter(User.id == user_id).one()
        challenge = self._get_login_challenge(user)
        if challenge is not None:
            return challenge
        return self.create_user_token(user, **kwargs)

    def _send_challenge_code(self, user):
        """E-mail code sent along with the challenge. A failure must not
        break the login: the user can request a new code or switch method"""
        try:
            VerificationCodeController(
                self.session, self._config).send_mfa_code(user)
            return True
        except ForbiddenException:
            LOG.info('MFA code for user %s not sent: throttled', user.id)
        except tornado.web.HTTPError:
            LOG.warning('MFA code for user %s not sent: herald unavailable',
                        user.id)
        return False

    def _get_login_challenge(self, user):
        """
        MFA decision after a successful password / recovery code check,
        under the user lock (read after it, so up to date):
        - confirmed methods -> mfa_required challenge
        - no method, but an organization enforces MFA -> enrollment_required
        - otherwise None (token issued as before)
        """
        challenges = LoginChallengeController(self.session, self._config)
        methods = MfaMethodController(
            self.session, self._config).get_confirmed_methods(user.id)
        if methods:
            challenge = challenges.create(
                user, LoginChallengeState.mfa_required)
            code_sent = False
            if methods[0].type == MFAType.email:
                code_sent = self._send_challenge_code(user)
            return challenges.to_response(challenge, methods, code_sent)
        policies = AuthPolicyController(self.session, self._config)
        if policies.is_mfa_enforced_for_user(user.id):
            challenge = challenges.create(
                user, LoginChallengeState.enrollment_required)
            return challenges.to_response(challenge, [])
        return None

    def _complete_challenge(self, challenge_id=None, code=None,
                            method_id=None, ip=None, **_):
        if code is None:
            raise_not_provided_error('code')
        for name, value in [('code', code), ('method_id', method_id)]:
            if value is not None and not isinstance(value, str):
                raise WrongArgumentsException(Err.OA0033, [name])
        challenges = LoginChallengeController(self.session, self._config)
        challenge = challenges.get_valid(challenge_id)
        if challenge.state == LoginChallengeState.enrollment_required:
            raise ForbiddenException(Err.OA0088, [])
        mfa_methods = MfaMethodController(self.session, self._config)
        methods = mfa_methods.get_confirmed_methods(challenge.user_id)
        method = next((m for m in methods if m.id == method_id),
                      None) if method_id else (methods[0] if methods else None)
        if method is None:
            raise NotFoundException(Err.OA0003, ['MFAMethod', method_id])
        challenge_id, user_id = challenge.id, challenge.user_id
        mfa = method.type.value
        challenges.verify_attempt(
            challenge_id, user_id,
            lambda: mfa_methods.verify_code(method, code))
        # consume and token in one transaction under the user lock: a
        # password change (same row) happens before (the challenge is gone)
        # or after (the token is signed with the old salt, so revoked)
        challenges.lock_user(user_id)
        challenges.consume(challenge_id, commit=False)
        user = challenges.get_active_user(user_id)
        token = self.create_user_token(user, mfa=mfa, ip=ip)
        challenges.reset_attempts(user_id)
        LOG.info('Login challenge completed for user %s with %s',
                 user_id, mfa)
        return token

    def create_token_by_user_id(self, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id is None:
            raise_not_provided_error('user_id')
        user = self.session.query(User).filter(
            and_(
                User.id == user_id,
                User.deleted.is_(False)
            )
        ).one_or_none()
        if not user:
            raise NotFoundException(Err.OA0043, [user_id])
        if not user.is_active:
            raise ForbiddenException(Err.OA0038, [])
        if not user.verified:
            raise ForbiddenException(Err.OA0073, [])
        return self.create_user_token(user, **kwargs)


class TokenAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return TokenController
