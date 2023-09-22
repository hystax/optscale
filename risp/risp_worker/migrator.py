import os
import hashlib
import importlib
import logging
from datetime import datetime
from clickhouse_driver import Client as ClickHouseClient

LOG = logging.getLogger(__name__)
MIGRATIONS_PATH = 'risp/risp_worker'
MIGRATIONS_FOLDER = 'migrations'
VERSIONS_TABLE = 'schema_versions'


class Migrator:

    DB_NAME = 'risp'

    def __init__(self, config_cl):
        self.config_cl = config_cl
        self._clickhouse_client = None

    def init_db(self):
        user, password, host, _ = self.config_cl.clickhouse_params()
        client = ClickHouseClient(
            host=host, password=password, user=user)
        client.execute(
            f"""CREATE DATABASE IF NOT EXISTS {self.DB_NAME}""")
        client.disconnect()

    @property
    def clickhouse_client(self):
        if self._clickhouse_client is None:
            user, password, host, _ = self.config_cl.clickhouse_params()
            self.init_db()
            self._clickhouse_client = ClickHouseClient(
                host=host, password=password, database=self.DB_NAME, user=user)
        return self._clickhouse_client

    def create_versions_table(self):
        self.clickhouse_client.execute(
            f"""CREATE TABLE IF NOT EXISTS {VERSIONS_TABLE} (
                 version UInt32,
                 md5 String,
                 script String,
                 created_at DateTime DEFAULT now())
               ENGINE = MergeTree
               ORDER BY tuple(created_at)""")

    def get_clickhouse_versions(self):
        versions_list = []
        ch_versions = self.clickhouse_client.execute(
            f"""SELECT script from {VERSIONS_TABLE}""")
        for ch_version in ch_versions:
            script_name = ch_version[0]
            # fix script names
            if script_name.endswith('sql'):
                new_script_name = script_name.replace('sql', 'py')
                self.clickhouse_client.execute(f"""
                    ALTER TABLE {VERSIONS_TABLE}
                    UPDATE script='{new_script_name}'
                    WHERE script='{script_name}'""")
                self.clickhouse_client.execute(
                    f"""OPTIMIZE TABLE {VERSIONS_TABLE} FINAL""")
            script_base_name = script_name.replace('.py', '').replace(
                f'{MIGRATIONS_FOLDER}/', '')
            versions_list.append(script_base_name)
        return sorted(versions_list)

    @staticmethod
    def get_local_versions():
        migrations_folder = os.path.join(
            os.getcwd(), MIGRATIONS_PATH, MIGRATIONS_FOLDER)
        migrations = []
        for filename in os.listdir(migrations_folder):
            if filename.startswith('V') and filename.endswith('.py'):
                migrations.append(filename.split('.py')[0])
        return sorted(migrations)

    @staticmethod
    def check_versions(local_versions, ch_versions):
        if len(local_versions) < len(ch_versions):
            raise ValueError(
                'Found remote migrations that do not exist locally. '
                'Did you accidentally remove something?'
            )
        for i, ch_version in enumerate(ch_versions):
            if ch_version != local_versions[i]:
                raise ValueError(
                    f'Found remote migrations that do not exist locally. '
                    f'Conflicting versions: ({ch_version}, {local_versions[i]})'
                )

    @staticmethod
    def _get_version_from_name(filename):
        return int(filename.split('_')[0].replace('V', ''))

    @staticmethod
    def _get_script_from_name(filename):
        return f'{MIGRATIONS_FOLDER}/{filename}.py'

    @staticmethod
    def _get_md5(filename):
        return hashlib.md5(open(
            f"{MIGRATIONS_FOLDER}/{filename}.py", 'rb').read()).hexdigest()

    def update_versions_table(self, filename):
        version = [{
            'version': self._get_version_from_name(filename),
            'md5': self._get_script_from_name(filename),
            'script': self._get_script_from_name(filename),
            'created_at': datetime.utcnow()
        }]
        self.clickhouse_client.execute(
            f"INSERT INTO {VERSIONS_TABLE} VALUES", version)

    def migrate(self):
        self.create_versions_table()
        local_versions = self.get_local_versions()
        ch_versions = self.get_clickhouse_versions()
        if ch_versions:
            LOG.info(
                'Found remote migrations. Last version is %s', ch_versions[-1])
        else:
            LOG.info('Found no remote migrations')
        self.check_versions(local_versions, ch_versions)
        pythonpath = os.environ['PYTHONPATH'].split(os.pathsep)[0]
        import_base = os.path.dirname(__file__)[len(pythonpath):]
        import_base = import_base.replace('/', '.')

        new_migrations = local_versions[len(ch_versions):]
        for filename in new_migrations:
            LOG.info('Upgrading version %s', filename)
            import_path = '%s.%s.%s' % (
                import_base, MIGRATIONS_FOLDER, filename)
            module = importlib.import_module(import_path)
            migration = module.Migration(self.config_cl)
            migration.upgrade()
            self.update_versions_table(filename)
            LOG.info('Finished migration %s', filename)
        LOG.info('Upgrade is finished')
