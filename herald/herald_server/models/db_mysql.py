from sqlalchemy import create_engine

from herald_server.models.db_base import BaseDB
from herald_server.models.migrator import Migrator


class MySQLDB(BaseDB):
    def _get_engine(self):
        return create_engine(
            'mysql+mysqlconnector://%s:%s@%s/%s' % (
                self._config.herald_db_params()),
            # inactive connections are invalidated by server
            # in ~10 minutes (600 seconds)
            pool_recycle=500,
            pool_size=25,
            max_overflow=10,
        )

    def create_schema(self):
        migrator = Migrator(self.engine)
        migrator.migrate_all()
