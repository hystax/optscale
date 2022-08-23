import logging
from pymongo import UpdateOne, UpdateMany
from diworker.migrations.base import BaseMigration

CHUNK_SIZE = 200
NAT_GATEWAY_TYPE = 'NAT Gateway'
LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def mongo_resources(self):
        return self.db.resources

    @property
    def mongo_expenses(self):
        return self.db.expenses

    @property
    def mongo_expenses_groupings(self):
        return self.db.expenses_group_month_resource

    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def upgrade(self):
        raw_expenses = self.mongo_raw.find({
            'lineItem/Operation': 'NatGateway',
            'product/productFamily': NAT_GATEWAY_TYPE}, ['_id']
        )
        raw_exp_ids = [x['_id'] for x in raw_expenses]
        pipeline = [
            {
                '$match': {'resource_type': {'$in': ['Instance']}}
            },
            {
                '$unwind': '$raw_data_links'
            },
            {
                '$match': {'raw_data_links': {'$in': raw_exp_ids}}
            }
        ]
        clean_expenses = self.mongo_expenses.aggregate(pipeline)
        resource_id_type_map = {}
        for exp in clean_expenses:
            if not resource_id_type_map.get(exp['resource_id']):
                resource_id_type_map[exp['resource_id']] = NAT_GATEWAY_TYPE

        exp_updates = []
        resource_updates = []
        for resource_id, resource_type in resource_id_type_map.items():
            exp_updates.append(UpdateMany(
                filter={'resource_id': resource_id},
                update={'$set': {'resource_type': resource_type}}))
            resource_updates.append(UpdateOne(
                filter={'_id': resource_id},
                update={'$set': {'resource_type': resource_type}}))

        for i in range(0, len(exp_updates), CHUNK_SIZE):
            self.mongo_expenses.bulk_write(exp_updates[i:i + CHUNK_SIZE])
            self.mongo_expenses_groupings.bulk_write(
                exp_updates[i:i + CHUNK_SIZE])
        for i in range(0, len(resource_updates), CHUNK_SIZE):
            self.mongo_resources.bulk_write(resource_updates[i:i + CHUNK_SIZE])

    def downgrade(self):
        pass
