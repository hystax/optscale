import logging
from diworker.diworker.migrations.base import BaseMigration


"""
Added cloud account report identity index
"""
INDEX_NAME = 'ReportIdentity'
INDEX_FIELDS = [
    'cloud_account_id',
    'start_date',
    'report_identity',
]
LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def delete_index(self):
        index_names = [x['name'] for x in self.mongo_raw.list_indexes()]
        if INDEX_NAME in index_names:
            LOG.info('Delete index %s' % INDEX_NAME)
            self.mongo_raw.drop_index(INDEX_NAME)

    def create_index(self):
        index_names = [x['name'] for x in self.mongo_raw.list_indexes()]
        if INDEX_NAME not in index_names:
            LOG.info('Create index %s' % INDEX_NAME)
            self.mongo_raw.create_index(
                [(f, 1) for f in INDEX_FIELDS],
                name=INDEX_NAME,
                background=True,
            )

    def upgrade(self):
        self.create_index()
        LOG.info('Migration complete')

    def downgrade(self):
        self.delete_index()
        LOG.info('Migration complete')
