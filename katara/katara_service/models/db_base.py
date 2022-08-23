from retrying import retry
from sqlalchemy.orm import sessionmaker, scoped_session

import katara_service.models.models as model_base


def should_retry(exception):
    return True


class BaseDB:
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

    @retry(stop_max_attempt_number=20, wait_fixed=1000,
           retry_on_exception=should_retry)
    def create_all(self):
        model_base.Base.metadata.create_all(self.engine)

    @property
    def engine(self):
        if not self._engine:
            self._engine = self._get_engine()
        return self._engine

    def _get_engine(self):
        raise NotImplementedError
