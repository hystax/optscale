import logging
import json
from sqlalchemy.sql import literal_column, and_
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.models.models import Organization, Pool

LOG = logging.getLogger(__name__)


class ResourceController(object):

    def __init__(self, db_session, config=None, token=None, engine=None):
        self.session = db_session
        self._config = config
        self._engine = engine
        self._db = None
        self.token = token

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, val):
        self._engine = val

    def resources_get(self, **kwargs):
        payload = kwargs.get('payload')
        try:
            li = json.loads(payload)
            if not isinstance(li, list):
                raise ValueError
            resource_ids = list(map(lambda x: x[1], li))
            query_set = self.session.query(
                literal_column(repr(Organization.__table__.name)).label(
                    "resource"),
                Organization.id, Organization.name
            ).filter(
                and_(
                    Organization.id.in_(resource_ids),
                    Organization.deleted_at.is_(False)
                )
            ).union(
                self.session.query(
                    literal_column(repr(Pool.__table__.name)).label(
                        "resource"),
                    Pool.id,
                    Pool.name,
                ).filter(
                    and_(
                        Pool.id.in_(resource_ids),
                        Pool.deleted_at.is_(False)))
            ).all()
            result = dict()
            for item in query_set:
                type_, id_, name = item
                result[id_] = {'name': name, 'type': type_}
            return result

        except (ValueError, json.decoder.JSONDecodeError) as ex:
            LOG.warning('Get resources: cannot load payload because of %s',
                        str(ex))
            return {}


class ResourceAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ResourceController
