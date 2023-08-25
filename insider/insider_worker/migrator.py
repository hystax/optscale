import logging
import os
import re
from datetime import datetime
from importlib import import_module

from pymongo import MongoClient

MIGRATIONS_COLLECTION_NAME = 'database_migrations'
LOCAL_MIGRATIONS_REGEX = r'^([0-9]+)[_a-z]*\.py$'
LOG = logging.getLogger(__name__)


class LocalMigration:
    def __init__(self, migration_datetime, file):
        self._datetime = migration_datetime
        self._file = file

    @property
    def datetime(self):
        return self._datetime

    @property
    def file(self):
        return self._file


class Migrator:
    def __init__(self, config_cl, database_name, migrations_path):
        self.config_cl = config_cl
        self.database_name = database_name
        self.migrations_path = migrations_path

        mongo_params = self.config_cl.mongo_params()
        mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
        self._mongo_cl = MongoClient(mongo_conn_string)

    @property
    def _mongo_migrations(self):
        return self._mongo_cl[self.database_name][MIGRATIONS_COLLECTION_NAME]

    def _get_remote_migrations(self):
        return list(self._mongo_migrations.find().sort('migration_datetime'))

    def _put_remote_migration(self, migration_datetime):
        self._mongo_migrations.insert_one({
            'migration_datetime': migration_datetime,
            'created_at': datetime.now()
        })

    def _delete_remote_migration(self, migration_datetime):
        self._mongo_migrations.delete_one({
            'migration_datetime': migration_datetime
        })

    def _get_local_migrations(self):
        migrations = []
        migrations_regex = re.compile(LOCAL_MIGRATIONS_REGEX)
        for file in os.listdir(self.migrations_path):
            result = migrations_regex.match(file)
            if result:
                migration = LocalMigration(result.group(1), file)
                migrations.append(migration)
        migrations.sort(key=lambda x: x.datetime)
        return migrations

    def _run_local_migration(self, migration, downgrade=False):
        try:
            module_name = os.path.splitext(migration.file)[0]
            module_path = os.path.join(self.migrations_path, module_name)
            module_path = os.path.normpath(module_path)
            module = import_module(module_path.replace(os.path.sep, '.'))
            migration_object = module.Migration(
                config_cl=self.config_cl,
                db=self._mongo_cl[self.database_name]
            )
            if downgrade:
                LOG.info('Downgrading version %s', migration.datetime)
                migration_object.downgrade()
            else:
                LOG.info('Upgrading version %s', migration.datetime)
                migration_object.upgrade()
        except Exception:
            LOG.error('Failed to apply version %s', migration.datetime)
            raise

    def _upgrade(self, local_migrations, remote_migrations, to_datetime=None):
        for local_migration in local_migrations:
            if to_datetime and local_migration.datetime > to_datetime:
                break
            if not remote_migrations or remote_migrations[-1][
                    'migration_datetime'] < local_migration.datetime:
                self._run_local_migration(local_migration)
                self._put_remote_migration(local_migration.datetime)

    def _downgrade(self, local_migrations, remote_migrations, to_datetime=None):
        remote_datetimes = {m['migration_datetime'] for m in remote_migrations}
        for local_migration in reversed(local_migrations):
            if to_datetime and local_migration.datetime <= to_datetime:
                break
            if local_migration.datetime in remote_datetimes:
                self._run_local_migration(local_migration, downgrade=True)
                self._delete_remote_migration(local_migration.datetime)

    def migrate(self, downgrade=False, to_datetime=None):
        LOG.info('Running MongoDB migrations')
        local_migrations = self._get_local_migrations()
        local_datetimes = {m.datetime for m in local_migrations}

        remote_migrations = self._get_remote_migrations()
        remote_datetimes = {m['migration_datetime'] for m in remote_migrations}
        if remote_datetimes - local_datetimes:
            raise ValueError(
                'Found remote migrations that do not exist locally. '
                'Did you accidentally remove something?'
            )

        if remote_migrations:
            LOG.info('Found remote migrations. Last version is %s',
                     remote_migrations[-1]['migration_datetime'])
        else:
            LOG.info('Found no remote migrations')

        if downgrade:
            self._downgrade(local_migrations, remote_migrations, to_datetime)
        else:
            self._upgrade(local_migrations, remote_migrations, to_datetime)
            if not to_datetime:
                remote_migrations = self._get_remote_migrations()
                remote_datetimes = {m['migration_datetime']
                                    for m in remote_migrations}
                if local_datetimes - remote_datetimes:
                    raise ValueError(
                        'Found more local migrations than were applied to '
                        'database. Did you forget to put your migration on top '
                        'after rebase?'
                    )
