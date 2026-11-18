import hmac
import logging

import pyotp
from sqlalchemy.exc import IntegrityError

from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.controllers.login_challenge import (
    LoginChallengeController)
from auth.auth_server.controllers.token_issuer import TokenIssuer
from auth.auth_server.controllers.verification_code import (
    VerificationCodeController)
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import (
    MFAMethod, MFAType, User, VerificationCodePurpose)
from auth.auth_server.utils import (
    TOTP_DIGITS, TOTP_PERIOD, build_otpauth_uri, check_kwargs_is_empty,
    check_string_attribute, decrypt_mfa_secret, encrypt_mfa_secret,
    mask_email)
from tools.optscale_exceptions.common_exc import (
    ConflictException, ForbiddenException, NotFoundException,
    WrongArgumentsException)
from tools.optscale_time import utcnow_timestamp

LOG = logging.getLogger(__name__)
# an enrollment not confirmed within this time is discarded
PENDING_LIFETIME_MIN = 15
# TOTP steps accepted before and after the current one (clock drift)
TOTP_VALID_WINDOW = 1
LABEL_MAX_LENGTH = 256


class MfaMethodController(BaseController):
    def _get_model_type(self):
        return MFAMethod

    def _check_access(self, user_id, token, challenge_id):
        """
        Owner's token or cluster secret, or (challenge_id) a valid
        enrollment_required login challenge of the same user: an enforced
        user without methods has no token yet. Returns (user, challenge).
        """
        if challenge_id is None:
            return self.check_user_access(user_id, token), None
        challenge = LoginChallengeController(
            self.session, self._config).get_enrollment_challenge(
                challenge_id, user_id)
        return challenge.user, challenge

    @staticmethod
    def _pending_cutoff():
        return utcnow_timestamp() - PENDING_LIFETIME_MIN * 60

    def _get_methods(self, user_id, type_=None):
        query = self.session.query(MFAMethod).filter(
            MFAMethod.user_id == user_id,
            MFAMethod.deleted.is_(False),
        )
        if type_ is not None:
            query = query.filter(MFAMethod.type == type_)
        return query.all()

    def get_confirmed_methods(self, user_id):
        return sorted(
            (m for m in self._get_methods(user_id) if m.confirmed),
            key=lambda m: (not m.is_default, m.created_at))

    def _has_confirmed_type(self, user_id, type_):
        # locking read: the latest committed rows (under the user lock)
        return self.session.query(MFAMethod.id).filter(
            MFAMethod.user_id == user_id,
            MFAMethod.type == type_,
            MFAMethod.deleted.is_(False),
            MFAMethod.confirmed_at != 0,
        ).with_for_update().first() is not None

    def _discard_stale_pending(self, user_id):
        # never-confirmed rows have no history worth keeping, so they are
        # removed instead of soft-deleted (this also avoids deleted_at
        # collisions on the user/type/deleted_at unique constraint)
        self.session.query(MFAMethod).filter(
            MFAMethod.user_id == user_id,
            MFAMethod.deleted.is_(False),
            MFAMethod.confirmed_at == 0,
            MFAMethod.created_at < self._pending_cutoff(),
        ).delete(synchronize_session=False)

    @staticmethod
    def _check_type(type_):
        if type_ is None:
            raise WrongArgumentsException(Err.OA0032, ['type'])
        if not isinstance(type_, str):
            raise WrongArgumentsException(Err.OA0033, ['type'])
        try:
            return MFAType(type_)
        except ValueError:
            raise WrongArgumentsException(Err.OA0060, ['type'])

    def create(self, user_id, token=None, challenge_id=None, **kwargs):
        """
        Starts an enrollment: creates a pending method of the given type.
        For totp the response carries the plain seed and the otpauth URI
        (the only time they are exposed), for email a code is sent to the
        user's address.
        """
        type_ = self._check_type(kwargs.pop('type', None))
        label = kwargs.pop('label', None)
        check_kwargs_is_empty(**kwargs)
        if label is not None:
            check_string_attribute('label', label,
                                   max_length=LABEL_MAX_LENGTH)
        user, challenge = self._check_access(user_id, token, challenge_id)
        user_id = user.id
        challenge_id = challenge.id if challenge is not None else None
        self._discard_stale_pending(user_id)
        if any(m.confirmed for m in self._get_methods(user_id, type_)):
            raise ConflictException(Err.OA0082, [type_.value])
        seed = None
        if type_ == MFAType.totp:
            seed = pyotp.random_base32()
            secret = encrypt_mfa_secret(seed)
        else:
            secret = None
            label = mask_email(user.email)
            # sent before anything is changed: if it is throttled or herald
            # is down, a previous pending enrollment is left untouched
            VerificationCodeController(
                self.session, self._config).send_mfa_code(user)
        # from here to the commit under the user lock, serialized with the
        # confirmations: checked again as things may have changed meanwhile
        challenges = LoginChallengeController(self.session, self._config)
        challenges.lock_user(user_id)
        if challenge_id is not None:
            try:
                challenges.get_enrollment_challenge(challenge_id, user_id)
            except (ForbiddenException, NotFoundException) as exc:
                challenges.abort(exc)
        if self._has_confirmed_type(user_id, type_):
            challenges.abort(ConflictException(Err.OA0082, [type_.value]))
        # restarting an unfinished enrollment replaces it; conditional, a
        # confirmed method is never removed
        self.session.query(MFAMethod).filter(
            MFAMethod.user_id == user_id,
            MFAMethod.type == type_,
            MFAMethod.deleted.is_(False),
            MFAMethod.confirmed_at == 0,
        ).delete(synchronize_session=False)
        user = self.session.query(User).filter(User.id == user_id).one()
        method = MFAMethod(user_id=user_id, type=type_, secret=secret,
                           label=label, is_default=False)
        self.session.add(method)
        try:
            self.session.commit()
        except IntegrityError:
            # concurrent enrollment of the same type
            self.session.rollback()
            raise ConflictException(Err.OA0082, [type_.value])
        LOG.info('MFA method %s (%s) enrollment started for user %s',
                 method.id, type_.value, user_id)
        result = method.to_dict()
        if seed is not None:
            result['secret'] = seed
            result['otpauth_uri'] = build_otpauth_uri(
                self._config.product_name(), user.email, seed)
        return result

    def _verify_totp(self, method, code):
        method_id = method.id
        totp = pyotp.TOTP(decrypt_mfa_secret(method.secret),
                          digits=TOTP_DIGITS, interval=TOTP_PERIOD)
        current = utcnow_timestamp() // TOTP_PERIOD
        for step in range(current - TOTP_VALID_WINDOW,
                          current + TOTP_VALID_WINDOW + 1):
            if not hmac.compare_digest(totp.generate_otp(step), code):
                continue
            # replay protection: a step is accepted only if it is newer than
            # the last accepted one; the conditional update makes it atomic
            # so two concurrent requests with the same code cannot both pass
            # (also 0 rows if the method was removed meanwhile; the object is
            # not refreshed: its row may be gone)
            updated = self.session.query(MFAMethod).filter(
                MFAMethod.id == method_id,
                MFAMethod.last_used_step < step,
            ).update({MFAMethod.last_used_step: step},
                     synchronize_session=False)
            self.session.commit()
            return updated == 1
        return False

    def _verify_email(self, method, code):
        used = self.use_verification_code(
            method.user.email, code, VerificationCodePurpose.mfa)
        self.session.commit()
        return bool(used)

    def verify_code(self, method, code):
        """
        Checks a code for the method. TOTP codes are accepted once
        (replay protection), e-mail codes are consumed.
        Reused by the login challenge (MPT-26346).
        """
        # isascii: isdigit() accepts other scripts' digits (e.g. Arabic-Indic)
        # and hmac.compare_digest raises TypeError on non-ASCII strings
        if not isinstance(code, str) or len(code) != TOTP_DIGITS or \
                not code.isascii() or not code.isdigit():
            return False
        if method.type == MFAType.totp:
            return self._verify_totp(method, code)
        return self._verify_email(method, code)

    def get_method(self, user_id, method_id):
        method = self.session.query(MFAMethod).filter(
            MFAMethod.id == method_id,
            MFAMethod.user_id == user_id,
            MFAMethod.deleted.is_(False),
        ).one_or_none()
        if method is None:
            raise NotFoundException(
                Err.OA0003, [MFAMethod.__name__, method_id])
        return method

    def _get_pending(self, method_id, for_update=False):
        query = self.session.query(MFAMethod).filter(
            MFAMethod.id == method_id,
            MFAMethod.deleted.is_(False),
            MFAMethod.confirmed_at == 0,
        )
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def _confirm_with_challenge(self, challenge, method, code, ip):
        """
        Enrollment of an enforced user signing in: the code check uses the
        attempts of the challenge, as the login does. Then, in one
        transaction under the user lock: the challenge is consumed (single
        use), the method confirmed as the first one, the other challenges
        revoked and the token created. Two challenges cannot both enroll a
        first method and a password change cannot interleave.
        """
        challenge_id, user_id = challenge.id, challenge.user_id
        method_id, mfa = method.id, method.type.value
        challenges = LoginChallengeController(self.session, self._config)

        def verify():
            # read again: the attempt commit expired the object and a new
            # enrollment may have replaced (removed) the pending method,
            # before or during the check
            pending = self._get_pending(method_id)
            if pending is not None and self.verify_code(pending, code):
                return True
            if self._get_pending(method_id) is None:
                raise NotFoundException(
                    Err.OA0003, [MFAMethod.__name__, method_id])
            return False
        challenges.verify_attempt(challenge_id, user_id, verify)
        challenges.lock_user(user_id)
        challenges.consume(challenge_id, commit=False)
        if challenges.has_confirmed_method(user_id, for_update=True):
            # another challenge enrolled a method in the meantime
            challenges.abort(ForbiddenException(Err.OA0089, []))
        method = self._get_pending(method_id, for_update=True)
        if method is None:
            # replaced by a new enrollment in the meantime
            challenges.abort(NotFoundException(
                Err.OA0003, [MFAMethod.__name__, method_id]))
        method.confirmed_at = utcnow_timestamp()
        method.is_default = True
        # the other challenges of the user cannot enroll anymore
        challenges.invalidate_user_challenges(user_id, exclude_id=challenge_id)
        user = challenges.get_active_user(user_id)
        # commits everything, releasing the lock
        token = TokenIssuer(self.session, self._config).create_user_token(
            user, mfa=mfa, ip=ip)
        token['user_email'] = user.email
        challenges.reset_attempts(user_id)
        LOG.info('MFA method %s (%s) confirmed for user %s', method_id, mfa,
                 user_id)
        LOG.info('Login challenge completed for user %s by enrollment',
                 user_id)
        return {'method': method.to_dict(), 'token': token}

    def confirm(self, user_id, method_id, token=None, challenge_id=None,
                ip=None, **kwargs):
        """
        Confirms a pending method. With a challenge (enforced user signing
        in) the challenge is consumed and a token is issued as well:
        returns {'method', 'token'} instead of the method.
        """
        code = kwargs.pop('code', None)
        check_kwargs_is_empty(**kwargs)
        if code is None:
            raise WrongArgumentsException(Err.OA0032, ['code'])
        if not isinstance(code, str):
            raise WrongArgumentsException(Err.OA0033, ['code'])
        user, challenge = self._check_access(user_id, token, challenge_id)
        method = self.get_method(user.id, method_id)
        if method.confirmed:
            raise ConflictException(Err.OA0084, [method_id])
        if method.created_at < self._pending_cutoff():
            # expired enrollment, it is discarded on the next create
            raise NotFoundException(
                Err.OA0003, [MFAMethod.__name__, method_id])
        if challenge is not None:
            return self._confirm_with_challenge(challenge, method, code, ip)
        user_id = user.id
        if not self.verify_code(method, code):
            LOG.info('Invalid code for MFA method %s of user %s',
                     method_id, user_id)
            raise ForbiddenException(Err.OA0083, [])
        # under the user lock, as the challenge mode: two concurrent
        # confirmations cannot both make their method the default one
        challenges = LoginChallengeController(self.session, self._config)
        challenges.lock_user(user_id)
        method = self._get_pending(method_id, for_update=True)
        if method is None:
            # replaced by a new enrollment in the meantime
            challenges.abort(NotFoundException(
                Err.OA0003, [MFAMethod.__name__, method_id]))
        has_confirmed = challenges.has_confirmed_method(user_id,
                                                        for_update=True)
        method.confirmed_at = utcnow_timestamp()
        method.is_default = not has_confirmed
        self.session.commit()
        LOG.info('MFA method %s (%s) confirmed for user %s', method_id,
                 method.type.value, user_id)
        return method


class MfaMethodAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return MfaMethodController
