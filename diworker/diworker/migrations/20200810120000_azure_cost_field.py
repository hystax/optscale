import logging
from pymongo import UpdateOne
from datetime import datetime, timezone
from diworker.migrations.base import BaseMigration

"""
Adds a 'cost' fields to all Azure raw expenses'.
Needed for calculating total cost with same logic as aws'.
"""

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200


class Migration(BaseMigration):

    def upgrade(self):
        update_requests = []
        filters = {
            'cost': {'$exists': False},
            'pretax_cost': {'$exists': True}
        }

        for item in self.db.raw_expenses.find(filters):
            update_request = UpdateOne(
                filter={'_id': item['_id']},
                update={'$set': {
                    'cost': float(item.get('pretax_cost', 0))
                }},
            )
            update_requests.append(update_request)
            if len(update_requests) == CHUNK_SIZE:
                self.db.raw_expenses.bulk_write(update_requests)
                update_requests = []

        if len(update_requests) > 0:
            self.db.raw_expenses.bulk_write(update_requests)

    def downgrade(self):
        update_requests = []
        filters = {
            'cost': {'$exists': True},
            'pretax_cost': {'$exists': True}
        }

        for item in self.db.raw_expenses.find(filters):
            update_request = UpdateOne(
                filter={'_id': item['_id']},
                update={'$unset':  {'cost': ''}}
            )
            update_requests.append(update_request)
            if len(update_requests) == CHUNK_SIZE:
                self.db.raw_expenses.bulk_write(update_requests)
                update_requests = []

        if len(update_requests) > 0:
            self.db.raw_expenses.bulk_write(update_requests)
