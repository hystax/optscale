from sqlalchemy.exc import IntegrityError
import time
import logging

from herald_server.exceptions import Err
from herald_server.models.models import PermissionKeys
from herald_server.utils import Config

from auth_client.client_v2 import Client as AuthClient
from optscale_exceptions.common_exc import WrongArgumentsException

LOG = logging.getLogger(__name__)


class BaseController(object):
    def __init__(self, db_session, config=None, rabbit_client=None):
        self._session = db_session
        self._config = config
        self.rabbit_client = rabbit_client
        self._db = None
        self._model_type = None
        self.auth_client = AuthClient(url=Config().auth_url,
                                      secret=Config().cluster_secret)

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, val):
        self._session = val

    @property
    def model_type(self):
        if self._model_type is None:
            self._model_type = self._get_model_type()
        return self._model_type

    def _get_model_type(self):
        raise NotImplementedError

    @property
    def model_column_list(self):
        return list(map(lambda x: str(x.name),
                        self.model_type.__table__.columns))

    @property
    def create_restrictions(self):
        return self._get_restrictions(PermissionKeys.is_creatable)

    @property
    def update_restrictions(self):
        return self._get_restrictions(PermissionKeys.is_updatable)

    def _get_restrictions(self, filter_by):
        res = list(
            map(lambda x: x.name, list(
                filter(lambda x: x.info.get(filter_by) is True,
                       self._get_model_type().__table__.c))))
        return res

    def check_update_restrictions(self, **kwargs):
        self._check_restrictions(self.update_restrictions, **kwargs)

    def check_create_restrictions(self, **kwargs):
        self._check_restrictions(self.create_restrictions, **kwargs)

    def _check_restrictions(self, restrictions, **kwargs):
        immutables = list(filter(
            lambda x: x not in restrictions, self.model_column_list))
        immutables_matches = list(filter(lambda x: x in kwargs, immutables))
        if immutables_matches:
            matches_string = ', '.join(immutables_matches)
            LOG.warning('immutable parameters %s: %s' %
                        (self.model_type, matches_string))
            raise WrongArgumentsException(Err.G0009, [matches_string])
        unexpected_params = list(filter(
            lambda x:
            x not in self.model_column_list and x not in restrictions,
            kwargs.keys()))
        if unexpected_params:
            unexpected_string = ', '.join(unexpected_params)
            LOG.warning('Unexpected parameters %s: %s' %
                        (self.model_type, unexpected_string))
            raise WrongArgumentsException(Err.G0010, [unexpected_string])

    def create(self, **kwargs):
        self.check_create_restrictions(**kwargs)
        model_type = self._get_model_type()
        LOG.info("Creating %s with parameters %s", model_type.__name__,
                 kwargs)

        item = model_type(**kwargs)

        self.session.add(item)
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.G0027, [str(ex)])
        return item

    def get(self, item_id, **kwargs):
        query = self.session.query(self.model_type).filter(
            self.model_type.id == item_id,
            self.model_type.deleted.is_(False))
        if len(kwargs) > 0:
            query = query.filter_by(**kwargs)
        res = query.all()
        if len(res) > 1:
            raise WrongArgumentsException(Err.G0011, [])
        if len(res) == 1:
            return res[0]

    def edit(self, item_id, **kwargs):
        self.check_update_restrictions(**kwargs)
        item = self.update(item_id, **kwargs)
        return item

    def update(self, item_id, **kwargs):
        try:
            item = self.get(item_id)
            if kwargs:
                self.session.expunge(item)
                for key, value in kwargs.items():
                    setattr(item, key, value)
                self.session.add(item)
                self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.G0027, [str(ex)])
        return item

    def delete(self, item_id):
        LOG.info("Deleting %s with id %s", self.model_type.__name__, item_id)
        self.update(item_id, deleted_at=time.time())

    def list(self, **kwargs):
        query = self.session.query(self.model_type).filter(
            self.model_type.deleted.is_(False))
        if len(kwargs) > 0:
            query = query.filter_by(**kwargs)
        return query.all()

    def authorize_users(self, user_ids, actions, object_type, object_id):
        _, authorized_users = self.auth_client.authorize_user_list(
            user_ids, actions, object_type, object_id)
        return authorized_users
