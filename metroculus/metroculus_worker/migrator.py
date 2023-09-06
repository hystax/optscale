import os
import logging
from migration_lib.migrate import migrate

LOG = logging.getLogger(__name__)
MIGRATIONS_PATH = 'metroculus/metroculus_worker/'
MIGRATIONS_FOLDER = 'migrations'


class Migrator:
    def __init__(self, config_cl):
        self.config_cl = config_cl

    def migrate(self):
        # migrations paths are used in schema_versions table, change directory
        # for backward compatibility
        curr_dir = os.getcwd()
        os.chdir(MIGRATIONS_PATH)
        user, password, host, db_name = self.config_cl.clickhouse_params()
        migrate(db_name, MIGRATIONS_FOLDER, host, user, password, True)
        os.chdir(curr_dir)
