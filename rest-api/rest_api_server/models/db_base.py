from sqlalchemy.orm import sessionmaker, scoped_session
from retrying import retry

from snapman_common.constants import DEFAULT_RETRY_ARGS
import rest_api_server.models.models as model_base


def should_retry(exception):
    return True


class BaseDB(object):
    def __init__(self, config=None):
        self._engine = None
        self._config = config

    @staticmethod
    def session(engine):
        """
        scoped session is a factory that maps results of scopefunc to sessions
        so if scopefunc returns request object, scoped_session returns
        the same session for a single request,
        but different sessions for different requests.
        """
        return scoped_session(sessionmaker(bind=engine))

    @retry(**DEFAULT_RETRY_ARGS, retry_on_exception=should_retry)
    def create_all(self):
        model_base.Base.metadata.create_all(self.engine)

    @property
    def engine(self):
        if not self._engine:
            self._engine = self._get_engine()
        return self._engine

    def _get_engine(self):
        raise NotImplementedError
