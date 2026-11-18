import logging

from sqlalchemy import func, or_

from auth.auth_server.controllers.base import BaseController
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import (
    LoginChallenge, LoginChallengeState, MFAMethod, User)
from tools.optscale_exceptions.common_exc import (
    ForbiddenException, NotFoundException, WrongArgumentsException)
from tools.optscale_time import utcnow_timestamp

LOG = logging.getLogger(__name__)
CHALLENGE_LIFETIME_MIN = 5
MAX_ATTEMPTS = 5
# attempts of all the challenges of a user within the window: a new login
# (new challenge) does not give more guesses for the same code
USER_MAX_ATTEMPTS = 10
USER_ATTEMPTS_WINDOW_MIN = 15


class LoginChallengeController(BaseController):
    """
    A login challenge is the proof that the password (or recovery code) of a
    user was verified while a second factor is still missing. It is not a
    token: it only allows completing the login (mfa_required) or enrolling
    the first method (enrollment_required), once, within a few minutes.
    """

    def _get_model_type(self):
        return LoginChallenge

    # the challenge id is a credential (it allows enrolling a method for an
    # enforced user): it is never logged

    @staticmethod
    def _window_start():
        """
        Creation time of the challenges whose attempts count. Attempts are
        made within the lifetime of a challenge, so the challenges created
        in the last window + lifetime include every attempt of the last
        window (older ones may be counted a bit longer: on the safe side).
        """
        return utcnow_timestamp() - (
            USER_ATTEMPTS_WINDOW_MIN + CHALLENGE_LIFETIME_MIN) * 60

    def _delete_old(self, user_id):
        # expired challenges are kept for the attempts window: their
        # attempts count for the user's budget
        self.session.query(LoginChallenge).filter(
            LoginChallenge.user_id == user_id,
            LoginChallenge.created_at < self._window_start(),
        ).delete(synchronize_session=False)

    def _recent_attempts(self, user_id):
        return self.session.query(
            func.coalesce(func.sum(LoginChallenge.attempts), 0)
        ).filter(
            LoginChallenge.user_id == user_id,
            LoginChallenge.created_at >= self._window_start(),
        ).scalar()

    def check_user_attempts(self, user_id):
        if self._recent_attempts(user_id) >= USER_MAX_ATTEMPTS:
            LOG.warning('MFA attempts limit reached for user %s', user_id)
            raise ForbiddenException(Err.OA0090, [])

    def abort(self, exc):
        """Rolls back (releasing the user lock) and raises exc"""
        self.session.rollback()
        raise exc

    def lock_user(self, user_id):
        """
        Locks the user row until the next commit. The current transaction
        is committed first: with MySQL REPEATABLE READ the snapshot of a
        transaction is taken at its first read, starting a new one with the
        lock guarantees the following reads see what the previous lock
        holder committed.
        """
        self.session.commit()
        self.session.query(User.id).filter(
            User.id == user_id).with_for_update().one()

    def get_active_user(self, user_id):
        """
        The user read again under the lock, before a token is issued: a
        user deactivated or deleted meanwhile gets OA0085 (rolled back)
        """
        user = self.session.query(User).filter(User.id == user_id).one()
        if user.deleted or not user.is_active:
            LOG.info('User %s deactivated during sign in', user_id)
            self.abort(NotFoundException(Err.OA0085, []))
        return user

    def lock_sign_in(self, user_id, salt):
        """
        Called right after the password check: locks the user row until the
        sign in commits its outcome (challenge or token), so the MFA
        decision is serialized with method confirmations and password
        changes, which take the same lock / update the same row.
        salt: the salt the password was checked with, it must still be the
        current one: a password changed meanwhile cannot leave a valid
        challenge or token obtained with the old password.
        """
        self.lock_user(user_id)
        current_salt = self.session.query(User.salt).filter(
            User.id == user_id).scalar()
        if current_salt != salt:
            LOG.info('Password of user %s changed during sign in', user_id)
            self.abort(ForbiddenException(Err.OA0037, []))

    def create(self, user, state):
        """Under the lock of lock_sign_in, released by the commit"""
        user_id = user.id
        self._delete_old(user_id)
        try:
            self.check_user_attempts(user_id)
        except ForbiddenException as exc:
            self.abort(exc)
        challenge = LoginChallenge(
            user_id=user.id, state=LoginChallengeState(state),
            expires_at=utcnow_timestamp() + CHALLENGE_LIFETIME_MIN * 60)
        self.session.add(challenge)
        self.session.commit()
        LOG.info('Login challenge (%s) created for user %s',
                 challenge.state.value, user.id)
        return challenge

    def get_valid(self, challenge_id):
        if not isinstance(challenge_id, str):
            raise WrongArgumentsException(Err.OA0033, ['challenge_id'])
        challenge = self.session.query(LoginChallenge).filter(
            *self._open_filter(challenge_id)).one_or_none()
        if challenge is None or challenge.user.deleted or \
                not challenge.user.is_active:
            raise NotFoundException(Err.OA0085, [])
        return challenge

    def has_confirmed_method(self, user_id, for_update=False):
        query = self.session.query(MFAMethod.id).filter(
            MFAMethod.user_id == user_id,
            MFAMethod.deleted.is_(False),
            MFAMethod.confirmed_at != 0,
        )
        if for_update:
            # locking read: the latest committed rows, not the snapshot
            query = query.with_for_update()
        return query.first() is not None

    def get_enrollment_challenge(self, challenge_id, user_id):
        """
        A valid enrollment_required challenge of the given user. It allows
        enrolling the first method only: once a method is confirmed the user
        must sign in again and verify it (mfa_required).
        """
        challenge = self.get_valid(challenge_id)
        if challenge.user_id != user_id or \
                challenge.state != LoginChallengeState.enrollment_required:
            raise ForbiddenException(Err.OA0012, [])
        if self.has_confirmed_method(user_id):
            raise ForbiddenException(Err.OA0089, [])
        return challenge

    def invalidate_user_challenges(self, user_id, exclude_id=None):
        """
        Discards the open challenges of a user (password changed, first
        method enrolled). Not committed: it is part of the caller's change.
        """
        query = self.session.query(LoginChallenge).filter(
            LoginChallenge.user_id == user_id,
            LoginChallenge.deleted.is_(False),
        )
        if exclude_id is not None:
            query = query.filter(LoginChallenge.id != exclude_id)
        return query.update({LoginChallenge.deleted_at: utcnow_timestamp()},
                            synchronize_session=False)

    # The methods below take ids, not the LoginChallenge object: after a
    # commit the object is expired and a concurrent completion may have
    # removed its row (reset_attempts), so reloading it would fail.

    @staticmethod
    def _open_filter(challenge_id):
        return (LoginChallenge.id == challenge_id,
                LoginChallenge.deleted.is_(False),
                LoginChallenge.expires_at > utcnow_timestamp())

    def register_attempt(self, challenge_id, user_id):
        """
        Reserves one attempt before a code is checked, so parallel requests
        cannot try more codes than allowed. Returns the attempts left.
        Raises OA0085 if the challenge is not open anymore, OA0087 if no
        attempts are left in the challenge, OA0090 if none are left for the
        user. The user row is locked so the attempts of concurrent
        challenges are counted correctly.
        """
        self.lock_user(user_id)
        try:
            self.check_user_attempts(user_id)
        except ForbiddenException as exc:
            self.abort(exc)
        updated = self.session.query(LoginChallenge).filter(
            *self._open_filter(challenge_id),
            LoginChallenge.attempts < MAX_ATTEMPTS,
        ).update({LoginChallenge.attempts: LoginChallenge.attempts + 1},
                 synchronize_session=False)
        # read in the same transaction, before the row can be removed
        attempts = self.session.query(LoginChallenge.attempts).filter(
            *self._open_filter(challenge_id)).scalar()
        if attempts is None:
            self.abort(NotFoundException(Err.OA0085, []))
        if not updated:
            self.abort(ForbiddenException(Err.OA0087, []))
        self.session.commit()
        return MAX_ATTEMPTS - attempts

    def verify_attempt(self, challenge_id, user_id, verify):
        """
        Checks a code (verify: callable returning bool) using one attempt
        of the challenge. A wrong code raises OA0086 with the attempts
        left, the last wrong code consumes the challenge and raises OA0087.
        """
        attempts_left = self.register_attempt(challenge_id, user_id)
        if verify():
            return
        LOG.info('Invalid code for a login challenge of user %s', user_id)
        if attempts_left <= 0:
            self.consume(challenge_id)
            raise ForbiddenException(Err.OA0087, [])
        raise ForbiddenException(Err.OA0086, [attempts_left])

    def consume(self, challenge_id, commit=True):
        """
        Single use: only one caller can consume an open (not expired)
        challenge, others get OA0085. With commit=False it is part of the
        caller's transaction (under the user lock, with the token).
        """
        updated = self.session.query(LoginChallenge).filter(
            *self._open_filter(challenge_id),
        ).update({LoginChallenge.deleted_at: utcnow_timestamp()},
                 synchronize_session=False)
        if not updated:
            self.abort(NotFoundException(Err.OA0085, []))
        if commit:
            self.session.commit()

    def reset_attempts(self, user_id):
        """
        After a successful verification the failures of the user are
        forgotten: used and expired challenges are removed (open ones of
        other sign ins are kept and still count).
        """
        self.session.query(LoginChallenge).filter(
            LoginChallenge.user_id == user_id,
            or_(LoginChallenge.deleted_at != 0,
                LoginChallenge.expires_at <= utcnow_timestamp()),
        ).delete(synchronize_session=False)
        self.session.commit()

    @staticmethod
    def to_response(challenge, methods, code_sent=False):
        default = next((m for m in methods if m.is_default),
                       methods[0] if methods else None)
        return {
            'challenge_id': challenge.id,
            'user_id': challenge.user_id,
            'state': challenge.state.value,
            'expires_at': challenge.expires_at,
            'user_email': challenge.user.email,
            'methods': [{
                'id': m.id,
                'type': m.type.value,
                'label': m.label,
                'is_default': m.is_default,
                'confirmed': m.confirmed,
            } for m in methods],
            'default_method_id': default.id if default else None,
            'code_sent': code_sent,
            'attempts_left': MAX_ATTEMPTS - challenge.attempts,
        }
