import logging

from auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth_server.models.models import Token
from auth_server.utils import load_payload, check_kwargs_is_empty

LOG = logging.getLogger(__name__)


class DigestController(object):
    def __init__(self, db_session, config=None):
        self._session = db_session
        self._config = config
        self._db = None

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, val):
        self._session = val

    def digest(self, **kwargs):
        payload = kwargs.pop('payload')
        check_kwargs_is_empty(**kwargs)
        payload_dict = load_payload(payload)
        digests = payload_dict.get('digests')
        token_metas = self.session.query(Token).filter(
            Token.digest.in_(digests)).all()
        result = dict(map(lambda k: (k, dict()), digests))
        for item in token_metas:
            result[item.digest] = {'user_name': item.user.email,
                                   'user_id': item.user.id,
                                   'user_display_name': item.user.display_name,
                                   'ip': item.ip,
                                   'token_created': item.created_at,
                                   'valid_until': item.valid_until.timestamp()}
        return result


class DigestAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return DigestController
