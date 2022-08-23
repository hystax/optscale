from migration_lib.migrate import migrate
import logging

LOG = logging.getLogger(__name__)
MIGRATIONS_PATH = 'migrations'


class Migrator:
    def __init__(self, config_cl):
        self.config_cl = config_cl

    def migrate(self):
        user, password, host, db_name = self.config_cl.clickhouse_params()
        migrate(db_name, MIGRATIONS_PATH, host, user, password, True)
