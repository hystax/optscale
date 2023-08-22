from pymongo import UpdateOne, UpdateMany
from diworker.diworker.migrations.base import BaseMigration

CHUNK_SIZE = 200


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
        raw_expenses = self.mongo_raw.find({'lineItem/LineItemType': 'Tax'},
                                           ['_id', 'lineItem/TaxType'])
        raw_exp_map = {x['_id']: x for x in raw_expenses}
        pipeline = [
            {
                '$match': {'resource_type': {'$in': ['Bucket', 'Instance',
                                                     'Volume']}}
            },
            {
                '$unwind': '$raw_data_links'
            },
            {
                '$match': {'raw_data_links': {'$in': list(raw_exp_map.keys())}}
            }
        ]
        clean_expenses = self.mongo_expenses.aggregate(pipeline)
        resource_id_type_map = {}
        for exp in clean_expenses:
            if not resource_id_type_map.get(exp['resource_id']):
                raw_exp = raw_exp_map.get(exp['raw_data_links'])
                resource_id_type_map[exp['resource_id']] = raw_exp['lineItem/TaxType']

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
