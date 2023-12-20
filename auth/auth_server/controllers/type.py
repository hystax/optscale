import logging
from sqlalchemy import and_

from tools.optscale_exceptions.common_exc import NotFoundException

from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import Type

LOG = logging.getLogger(__name__)


class TypeController(BaseController):
    def _get_model_type(self):
        return Type

    def create(self, **kwargs):
        raise NotImplementedError

    def get(self, item_id, **kwargs):
        token = kwargs.get('token')
        self.get_user(token)  # will raise 401 if token isn't valid
        item = self.session.query(Type).filter(
            and_(
                Type.id == item_id,
                Type.deleted.is_(False)
            )).one_or_none()

        if not item:
            raise NotFoundException(Err.OA0056, [item_id])

        return item

    def list(self, **kwargs):
        by_secret = kwargs.pop('by_secret', None)
        if not by_secret:
            token = kwargs.get('token')
            self.get_user(token)  # will raise 401 if token isn't valid
        return self.session.query(Type).filter(
            Type.deleted.is_(False)).all()


class TypeAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return TypeController
