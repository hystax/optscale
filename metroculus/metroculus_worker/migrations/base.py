import os
from clickhouse_driver import Client as ClickHouseClient


CH_DB_NAME = 'default'
MIGRATIONS_FOLDER = 'migrations'


class MigrationBase:
    def __init__(self, config_client):
        self.config_client = config_client
        self._mongo_client = None
        self._clickhouse_client = None

    @property
    def name(self):
        return os.path.basename(__file__)

    @property
    def migrations_path(self):
        return os.path

    @property
    def clickhouse_client(self):
        if self._clickhouse_client is None:
            user, password, host, _ = self.config_client.clickhouse_params()
            self._clickhouse_client = ClickHouseClient(
                host=host, password=password, database=CH_DB_NAME, user=user)
        return self._clickhouse_client

    def upgrade(self):
        raise NotImplementedError
