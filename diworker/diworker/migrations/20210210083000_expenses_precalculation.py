import logging
from pymongo import UpdateOne
from datetime import timezone
from calendar import month_name
from diworker.diworker.migrations.base import BaseMigration
from diworker.diworker.utils import get_month_start, retry_mongo_upsert

"""
Creates 'expenses_group_month_resource' and 'expenses_group_month_ca'
collections and their indexes. Also creates documents for existing expenses.
"""

MONTH_RESOURCE_INDEXES = {
        'ResourceID': (['resource_id'], False),
        'ResourceDate': (['resource_id', 'date'], True),
        'BudgetDate': (['budget_id', 'date'], False),
        'CloudAccountDate': (['cloud_account_id', 'date'], False),
        'CloudAccountBudget': (['cloud_account_id', 'budget_id'], False)
    }
MONTH_CA_INDEXES = {
    'CloudAccountDate': (['cloud_account_id', 'date'], True)
}
CHUNK_SIZE = 2000
LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def mongo_clean(self):
        return self.db.expenses

    @property
    def mongo_group_month_resource(self):
        return self.db.expenses_group_month_resource

    @property
    def mongo_group_month_ca(self):
        return self.db.expenses_group_month_ca

    def create_group_month_resource_indexes(self):
        existing_indexes = [
            x['name'] for x in self.mongo_group_month_resource.list_indexes()
        ]
        for index_name, index in MONTH_RESOURCE_INDEXES.items():
            fields, unique = index
            if index_name in existing_indexes:
                continue
            self.mongo_group_month_resource.create_index(
                [(f, 1) for f in fields],
                name=index_name, unique=unique
            )

    def create_group_month_ca_indexes(self):
        existing_indexes = [
            x['name'] for x in self.mongo_group_month_ca.list_indexes()
        ]
        for index_name, index in MONTH_CA_INDEXES.items():
            fields, unique = index
            if index_name in existing_indexes:
                continue
            self.mongo_group_month_ca.create_index(
                [(f, 1) for f in fields],
                name=index_name, unique=unique
            )

    def save_month_chunk(self, resources_chunk):
        cloud_accounts_chunk = {}
        for i in range(0, len(resources_chunk), CHUNK_SIZE):
            chunk = resources_chunk[i:i + CHUNK_SIZE]
            for c in chunk:
                ca_id = c['cloud_account_id']
                if not cloud_accounts_chunk.get(ca_id):
                    cloud_accounts_chunk[ca_id] = {
                        'cloud_account_id': ca_id,
                        'date': c['date'],
                        'cost': 0,
                        'count': 0
                    }
                cloud_accounts_chunk[ca_id]['count'] += 1
                cloud_accounts_chunk[ca_id]['cost'] += c['cost']
            retry_mongo_upsert(self.mongo_group_month_resource.bulk_write, [
                UpdateOne(
                    filter={
                        'resource_id': r['resource_id'],
                        'date': r['date']
                    },
                    update={
                        '$set': {k: v for k, v in r.items()}
                    },
                    upsert=True
                ) for r in chunk
            ])
        retry_mongo_upsert(self.mongo_group_month_ca.bulk_write, [
            UpdateOne(
                filter={
                    'cloud_account_id': c['cloud_account_id'],
                    'date': c['date']
                },
                update={
                    '$set': {k: v for k, v in c.items()}
                },
                upsert=True
            ) for c in cloud_accounts_chunk.values()
        ])

    def create_precalculated_records(self):
        month_chunk = {}
        chunk_date = None
        resource_fields = [
            'resource_id', 'cloud_account_id', 'budget_id', 'owner_id',
            'region', 'resource_type', 'service_name', 'cloud_resource_id'
        ]
        for expense in self.mongo_clean.find({}).sort('date', 1):
            date = get_month_start(expense['date'], timezone.utc)
            if date != chunk_date:
                chunk_date = date
                LOG.info('Processing %s %s' % (
                    month_name[chunk_date.month], chunk_date.year))
                if month_chunk:
                    self.save_month_chunk(list(month_chunk.values()))
                    month_chunk = {}
            resource_id = expense['resource_id']
            resource = month_chunk.get(resource_id)
            if not resource:
                resource_info = {'date': chunk_date, 'cost': 0}
                resource_info.update(
                    {k: expense.get(k) for k in resource_fields})
                month_chunk.update({resource_id: resource_info})
            month_chunk[resource_id]['cost'] += expense['cost']
        if month_chunk:
            self.save_month_chunk(list(month_chunk.values()))

    def upgrade(self):
        self.create_group_month_resource_indexes()
        self.create_group_month_ca_indexes()
        self.create_precalculated_records()

    def downgrade(self):
        self.mongo_group_month_resource.drop()
        self.mongo_group_month_ca.drop()
