from diworker.diworker.migrations.base import BaseMigration

"""
Adds indexes for fields in expenses collection.
We do a lot of queries and can use all of them for filtering, but we only had
indexes for cloud_resource_id and unique index
(resource_id,date,cloud_account_id). Last one used by diworker, but can't be
used in other places (only for resource_id or resource_id,date) filters. So I
added explicitly indexes for all other fields.
"""

INDEXES = [
    ('CloudAccountId', 'cloud_account_id'),
    ('Date', 'date'),
    ('ResourceId', 'resource_id'),
    ('BudgetId', 'budget_id'),
    ('OwnerId', 'owner_id'),
    ('Region', 'region'),
    ('ResourceType', 'resource_type'),
    ('ServiceName', 'service_name'),
]


class Migration(BaseMigration):
    @property
    def mongo_clean(self):
        return self.db.expenses

    def upgrade(self):
        index_names = [x['name'] for x in self.mongo_clean.list_indexes()]
        for new_index_name, field in INDEXES:
            if new_index_name not in index_names:
                self.mongo_clean.create_index([(field, 1)], name=new_index_name)

    def downgrade(self):
        index_names = [x['name'] for x in self.mongo_clean.list_indexes()]
        for index_name, _ in INDEXES:
            if index_name in index_names:
                self.mongo_clean.drop_index(index_name)
