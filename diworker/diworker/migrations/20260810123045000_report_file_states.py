import logging
from diworker.diworker.migrations.base import BaseMigration

"""
Adds index for report_import_files collection.
"""

LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def mongo_report_files(self):
        return self.db.report_import_files

    def upgrade(self):
        self.mongo_report_files.create_index(
            [('cloud_account_id', 1), ('file_key', 1)],
            unique=True,
            name='cloud_account_id_file_key_unique',
            background=True
        )
        LOG.info('Created report_import_files collection with unique index')

    def downgrade(self):
        self.db.drop_collection('report_import_files')
        LOG.info('Dropped report_import_files collection')
