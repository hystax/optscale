from diworker.migrations.base import BaseMigration

"""
Adds a 'cloud_resource_id' field to clean expenses.
"""

INDEX_NAME = 'CloudResourceId'


class Migration(BaseMigration):
    @property
    def mongo_clean(self):
        return self.db.expenses

    def upgrade(self):
        self.mongo_clean.create_index(
            [('cloud_resource_id', 1)], name=INDEX_NAME)

    def downgrade(self):
        indexes = [x['name'] for x in self.mongo_clean.list_indexes()]
        if INDEX_NAME in indexes:
            self.mongo_clean.drop_index(INDEX_NAME)
