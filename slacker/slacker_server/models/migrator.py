import logging
import os

from alembic import autogenerate
from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory

from slacker.slacker_server.models.db_base import get_db_metadata

target_metadata = get_db_metadata()
LOG = logging.getLogger(__name__)


class Migrator:
    """
    Class that makes updates database according to migrations
    """

    def __init__(self, engine):
        self._engine = engine
        self.engine_url = str(self._engine.url)
        self.alembic_cfg = Config()
        self.alembic_cfg.set_main_option(
            "script_location",
            os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         '..', 'alembic'))
        self.alembic_cfg.set_main_option("url", self.engine_url)
        self.alembic_script = ScriptDirectory.from_config(self.alembic_cfg)
        self.alembic_env = EnvironmentContext(self.alembic_cfg,
                                              self.alembic_script)

    def do_upgrade(self, revision, context):
        """
        Do upgrade for alembic coontext
        :param revision:
        :param context:
        :return:
        """
        return self.alembic_script._upgrade_revs(
            self.alembic_script.get_heads(), revision)

    def migrate(self):
        """
        Do migrations
        :return:
        """
        LOG.debug('Migrating database for %s', self.engine_url)
        conn = self._engine.connect()
        self.alembic_env.configure(connection=conn,
                                   target_metadata=target_metadata)

        alembic_context = self.alembic_env.get_context()
        LOG.debug(
            "Pending migrations for %s: %s", self.engine_url,
            autogenerate.compare_metadata(alembic_context, target_metadata))
        # TODO: do we really need to produce migrations here
        # autogenerate.produce_migrations(alembic_context, target_metadata)
        self.alembic_env.configure(connection=conn,
                                   target_metadata=target_metadata,
                                   fn=self.do_upgrade)
        with self.alembic_env.begin_transaction():
            self.alembic_env.run_migrations()

    def migrate_all(self):
        try:
            self.migrate()
        except Exception as ex:
            LOG.error("Failed to apply migrations with error %s", str(ex))
            raise
