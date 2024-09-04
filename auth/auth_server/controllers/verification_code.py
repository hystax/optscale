import logging
from datetime import datetime, timedelta
from sqlalchemy import and_, exists
from sqlalchemy.exc import IntegrityError
from auth.auth_server.controllers.base import BaseController
from auth.auth_server.models.models import VerificationCode
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import User
from auth.auth_server.utils import get_digest
from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  ForbiddenException)

LOG = logging.getLogger(__name__)
VERIFICATION_CODE_LIFETIME_HRS = 1
GENERATION_THRESHOLD_MIN = 1


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

    def _check_generation_timeout(self, email):
        model = self._get_model_type()
        timeout = datetime.utcnow() - timedelta(
            minutes=GENERATION_THRESHOLD_MIN)
        code_exists = self.session.query(exists().where(and_(
            model.email == email,
            model.created_at >= int(timeout.timestamp())
        ))).scalar()
        if code_exists:
            raise ForbiddenException(Err.OA0072, [])

    def create(self, **kwargs):
        self.check_create_restrictions(**kwargs)
        self._check_input(**kwargs)
        return self.create_verification_code(**kwargs)

    def _invalidate_verification_codes(self, email, deleted_at):
        model = self._get_model_type()
        self.session.query(model).filter(
            model.email == email,
            model.deleted.is_(False)
        ).update({
            model.deleted_at: deleted_at
        })

    def create_verification_code(self, email, code):
        model_type = self._get_model_type()
        LOG.info("Creating %s for %s", model_type.__name__, email)
        now = datetime.utcnow()
        now_ts = int(now.timestamp())
        params = {
            'email': email,
            'created_at': now_ts,
            'valid_until': now + timedelta(
                hours=VERIFICATION_CODE_LIFETIME_HRS),
            'code': get_digest(str(code)),
        }
        verification_code = model_type(**params)
        self._invalidate_verification_codes(email, now_ts)
        self.session.add(verification_code)
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OA0061, [str(ex)])
        return verification_code


class VerificationCodeAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return VerificationCodeController
