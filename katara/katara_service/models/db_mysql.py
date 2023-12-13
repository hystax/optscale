from sqlalchemy import create_engine

from katara.katara_service.models.db_base import BaseDB
from katara.katara_service.models.migrator import Migrator


class MySQLDB(BaseDB):
    def _get_engine(self):
        user, password, host, db = self._config.katara_db_params()
        return create_engine(
            f'mysql+mysqlconnector://{user}:{password}@{host}/{db}'
            f'?charset=utf8mb4',
            # inactive connections are invalidated in ~10 minutes (600 seconds)
            pool_recycle=500,
            pool_size=200,
            max_overflow=25,
        )

    def create_schema(self):
        migrator = Migrator(self.engine)
        migrator.migrate_all()
