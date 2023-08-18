"""
First/last expenses in grouped collections
"""
import logging
from calendar import monthrange
from datetime import datetime, timedelta

from diworker.diworker.migrations.base import BaseMigration
from pymongo import UpdateOne

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 1000


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

    @staticmethod
    def get_max_last_expense():
        return (datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1))

    @staticmethod
    def set_first_last_expenses(collection, info, months_list, grouping_field):
        updates = []
        for resource_info in info:
            first_month = resource_info['first_expense'].replace(
                day=1, hour=0, minute=0, second=0, microsecond=0)
            last_month = resource_info['last_expense'].replace(
                day=1, hour=0, minute=0, second=0, microsecond=0)
            for start_month, end_month in months_list:
                first_expense = resource_info['first_expense'] if (
                        start_month == first_month) else start_month
                last_expense = min(end_month, resource_info['last_expense']) if (
                        start_month == last_month) else end_month
                updates.append(UpdateOne(
                    filter={grouping_field: resource_info['_id'],
                            'date': start_month},
                    update={'$set': {
                        'first_expense': first_expense,
                        'last_expense': last_expense}}))
                if len(updates) >= CHUNK_SIZE:
                    collection.bulk_write(updates)
                    updates.clear()
        if len(updates):
            collection.bulk_write(updates)

    @staticmethod
    def unset_first_last_expenses(collection):
        records = collection.find({}, {'_id': True})
        bulk_ids = []
        for record in records:
            bulk_ids.append(record['_id'])
            if len(bulk_ids) >= CHUNK_SIZE:
                collection.update_many(
                    filter={'_id': {'$in': bulk_ids}},
                    update={'$unset': {'first_expense': '', 'last_expense': ''}})
                bulk_ids.clear()
        if len(bulk_ids):
            collection.update_many(
                filter={'_id': {'$in': bulk_ids}},
                update={'$unset': {'first_expense': '', 'last_expense': ''}})

    def get_months_list(self, group_ca_collection, ca_id):
        pipeline = [
            {'$match': {'cloud_account_id': ca_id}},
            {'$group': {'_id': '$date'}}
        ]
        db_months = group_ca_collection.aggregate(pipeline)
        months = []
        max_last = self.get_max_last_expense()
        for month in db_months:
            months.append((month['_id'], min(month['_id'].replace(
                day=monthrange(month['_id'].year, month['_id'].month)[1]), max_last)))
        return months

    @staticmethod
    def get_ca_list(group_ca_collection):
        pipeline = [
            {'$group': {
                '_id': '$cloud_account_id'
            }}
        ]
        return [x['_id'] for x in group_ca_collection.aggregate(pipeline)]

    def upgrade(self):
        ca_list = self.get_ca_list(self.mongo_group_month_ca)
        ca_count = len(ca_list)
        for collection in [self.mongo_group_month_resource,
                           self.mongo_group_month_ca]:
            grouping_field = 'cloud_account_id' if (
                    collection == self.mongo_group_month_ca
            ) else 'resource_id'
            LOG.info('Collection processing started')
            count = 0
            for ca_id in ca_list:
                months_list = self.get_months_list(
                    self.mongo_group_month_ca, ca_id)
                pipeline = [
                    {'$match': {
                        'cloud_account_id': ca_id
                    }},
                    {'$group': {
                        '_id': "$%s" % grouping_field,
                        'first_expense': {'$min': '$date'},
                        'last_expense': {'$max': '$date'}
                    }}
                ]
                info = self.mongo_clean.aggregate(pipeline, allowDiskUse=True)
                self.set_first_last_expenses(
                    collection, info, months_list, grouping_field)
                count += 1
                LOG.info('Processed %s of %s cloud accounts', count, ca_count)

    def downgrade(self):
        for collection in [self.mongo_group_month_resource,
                           self.mongo_group_month_ca]:
            self.unset_first_last_expenses(collection)
