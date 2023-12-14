from sqlalchemy import create_engine

from auth.auth_server.models.db_base import BaseDB
from auth.auth_server.models.migrator import Migrator


class MySQLDB(BaseDB):
    def _get_engine(self):
        user, password, host, db = self._config.auth_db_params()
        return create_engine(
            f'mysql+mysqlconnector://{user}:{password}@{host}/{db}'
            f'?charset=utf8mb4',
            # inactive connections are invalidated by server
            # in ~10 minutes (600 seconds)
            pool_recycle=500,
            pool_size=25,
            max_overflow=10,
        )

    def create_schema(self):
        migrator = Migrator(self.engine)
        migrator.migrate_all()
