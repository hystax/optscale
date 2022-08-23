import logging
from sqlalchemy.exc import IntegrityError

from katara_service.exceptions import Err
from katara_service.models.models import PermissionKeys
from katara_service.models.db_base import BaseDB

from optscale_exceptions.common_exc import WrongArgumentsException


LOG = logging.getLogger(__name__)


class BaseController(object):

    def __init__(self, db_session=None, config=None, engine=None):
        self._session = db_session
        self._config = config
        self._db = None
        self._model_type = None
        self._engine = engine

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        if not self._session:
            self._session = BaseDB.session(self._engine)()
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

    def _get_create_restrictions(self):
        return self._get_restrictions(PermissionKeys.is_creatable)

    def _get_update_restrictions(self):
        return self._get_restrictions(PermissionKeys.is_updatable)

    def _get_restrictions(self, filter_by):
        res = list(
            map(lambda x: x.name, list(
                filter(lambda x: x.info.get(filter_by) is True,
                       self._get_model_type().__table__.c))))
        return res

    def check_update_restrictions(self, **kwargs):
        self._check_restrictions(self._get_update_restrictions(), **kwargs)

    def check_create_restrictions(self, **kwargs):
        self._check_restrictions(self._get_create_restrictions(), **kwargs)

    def _check_immutables(self, restrictions, **kwargs):
        immutables = list(filter(
            lambda x: x not in restrictions, self.model_column_list))
        immutables_matches = list(filter(lambda x: x in kwargs, immutables))
        if immutables_matches:
            message = ', '.join(immutables_matches)
            LOG.warning('Immutable parameters %s: %s' %
                        (self.model_type, message))
            raise WrongArgumentsException(Err.OKA0019, [message])

    def _check_restrictions(self, restrictions, **kwargs):
        self._check_immutables(restrictions, **kwargs)
        unexpected_params = list(filter(
            lambda x:
            x not in self.model_column_list and x not in restrictions,
            kwargs.keys()))
        if unexpected_params:
            message = ', '.join(unexpected_params)
            LOG.warning('Unexpected parameters %s: %s' %
                        (self.model_type, message))
            raise WrongArgumentsException(Err.OKA0012, [message])

    def _validate(self, item, is_new=True, **kwargs):
        pass

    def create(self, **kwargs):
        self.check_create_restrictions(**kwargs)
        model_type = self._get_model_type()
        item = model_type(**kwargs)
        self._validate(item, is_new=True, **kwargs)
        LOG.info("Creating %s with parameters %s", model_type.__name__,
                 kwargs)

        self.session.add(item)
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OKA0017, [str(ex)])
        return item

    def get(self, item_id):
        return self.session.query(self.model_type).get(item_id)

    def edit(self, item_id, **kwargs):
        self.check_update_restrictions(**kwargs)
        try:
            item = self.get(item_id)
            if kwargs:
                self.session.expunge(item)
                for key, value in kwargs.items():
                    setattr(item, key, value)
                self._validate(item, is_new=False, **kwargs)
                self.session.add(item)
                self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OKA0017, [str(ex)])
        return item

    def delete(self, item_id):
        LOG.info("Deleting %s with id %s", self.model_type.__name__, item_id)
        self.session.query(self.model_type).filter_by(
            id=item_id).delete(synchronize_session='fetch')
        self.session.commit()

    def list(self, **kwargs):
        query = self.session.query(self.model_type)
        if len(kwargs) > 0:
            query = query.filter_by(**kwargs)
        return query.all()
