from pymongo import UpdateOne

from diworker.diworker.migrations.base import BaseMigration

"""
Adds a 'resource_id' field to all raw expenses that have 'lineItem/ResourceId'.
Search by 'resource_id' is faster than regex search on 'lineItem/ResourceId'.
"""

CHUNK_SIZE = 200


class Migration(BaseMigration):
    def upgrade(self):
        update_requests = []
        filters = {
            'resource_id': {'$exists': False},
            'lineItem/ResourceId': {'$exists': True},
        }

        for item in self.db.raw_expenses.find(filters):
            update_request = UpdateOne(
                filter={'_id': item['_id']},
                update={'$set': {
                    'resource_id': item['lineItem/ResourceId'].split('/')[-1]}
                },
            )
            update_requests.append(update_request)
            if len(update_requests) == CHUNK_SIZE:
                self.db.raw_expenses.bulk_write(update_requests)
                update_requests = []

        if len(update_requests) > 0:
            self.db.raw_expenses.bulk_write(update_requests)

    def downgrade(self):
        self.db.raw_expenses.update_many({}, {'$unset': {'resource_id': ''}})
