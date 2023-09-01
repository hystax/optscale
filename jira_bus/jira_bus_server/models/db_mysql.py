from sqlalchemy import create_engine

from jira_bus.jira_bus_server.models.db_base import BaseDB
from jira_bus.jira_bus_server.models.migrator import Migrator


class MySQLDB(BaseDB):
    def _get_engine(self):
        return create_engine(
            "mysql+mysqlconnector://%s:%s@%s/%s" % self._config.jira_bus_db_params(),
            # inactive connections are invalidated in ~10 minutes (600 seconds)
            pool_recycle=500,
            pool_size=200,
            max_overflow=25,
        )

    def create_schema(self):
        migrator = Migrator(self.engine)
        migrator.migrate_all()
