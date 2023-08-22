import logging

from diworker.diworker.migrations.base import BaseMigration

"""
Adds an index for 'instance_id' field to increase search speed on Azure raw data
"""

LOG = logging.getLogger(__name__)
INDEX_FIELD = 'instance_id'


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def create_instance_id_index(self):
        existing_indexes = [x['name'] for x in self.mongo_raw.list_indexes()]
        if INDEX_FIELD not in existing_indexes:
            LOG.info('Creating search index %s in raw collection', INDEX_FIELD)
            self.mongo_raw.create_index([(INDEX_FIELD, 1)], name=INDEX_FIELD)

    def upgrade(self):
        self.create_instance_id_index()

    def downgrade(self):
        self.mongo_raw.drop_index(INDEX_FIELD)
