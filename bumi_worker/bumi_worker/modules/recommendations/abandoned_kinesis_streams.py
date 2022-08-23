import logging
from collections import OrderedDict
from datetime import datetime, timedelta

from bumi_worker.modules.base import ModuleBase

SUPPORTED_CLOUD_TYPES = [
    'aws_cnr'
]

LOG = logging.getLogger(__name__)
DEFAULT_DAYS_THRESHOLD = 7


class AbandonedKinesisStreams(ModuleBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {
                'default': DEFAULT_DAYS_THRESHOLD},
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []}
        })

    def _get_abandoned_kinesis_streams(self, ca_ids, start_date, active_date):
        pipeline = [
            {
                '$match':
                    {
                        'cloud_account_id': {'$in': ca_ids},
                        'end_date': {'$gt': start_date},
                        'cost': {'$gt': 0},
                        'pricing/term': 'OnDemand',
                        'product/servicecode': 'AmazonKinesis'
                    }
            },
            {
                '$sort': {'end_date': -1}
            },
            {
                '$group':
                    {
                        '_id': {
                            'cloud_account_id': '$cloud_account_id',
                            'cloud_resource_id': '$resource_id'
                        },
                        'operation': {'$addToSet': '$lineItem/Operation'},
                        'cost': {'$first': '$cost'},
                        'price': {'$first': '$pricing/publicOnDemandRate'},
                        'last_start': {'$first': '$start_date'},
                        'last_end': {'$first': '$end_date'}
                    }
            },
            {
                '$match':
                    {
                        'last_end': {'$gte': active_date},
                        'operation': ['shardHourStorage']
                    }
            }
        ]
        return self.mongo_client.restapi.raw_expenses.aggregate(pipeline, hint="AwsServiceName")

    def _get_resources_info(self, resource_ids, start_date):
        return self.mongo_client.restapi.resources.find({
            '$or': resource_ids, 'first_seen': {'$lte': start_date}
        }) if resource_ids else []

    def _get(self):
        (days_threshold, excluded_pools,
         skip_cloud_accounts) = self.get_options_values()
        cloud_accounts_map = self.get_cloud_accounts(SUPPORTED_CLOUD_TYPES,
                                                     skip_cloud_accounts)
        employees = self.get_employees()
        pools = self.get_pools()

        last_import_map = {}
        for ca_id, ca in cloud_accounts_map.items():
            last_import_day = datetime.fromtimestamp(
                ca['last_import_at']).replace(
                hour=0, minute=0, second=0, microsecond=0)
            if not last_import_map.get(last_import_day):
                last_import_map[last_import_day] = []
            last_import_map[last_import_day].append(ca_id)

        result = []
        for last_import, ca_ids in last_import_map.items():
            expense_map = {}
            resource_ids = []
            active_date = last_import - timedelta(
                days=2)
            start_date_raw_expenses = last_import - timedelta(
                days=days_threshold)
            start_date_resources = start_date_raw_expenses.timestamp()
            expenses = self._get_abandoned_kinesis_streams(
                ca_ids, start_date_raw_expenses, active_date)
            for row in expenses:
                resource_id = row.pop('_id')
                ca_id = resource_id['cloud_account_id']
                cr_id = resource_id['cloud_resource_id']
                if ca_id not in expense_map:
                    expense_map[ca_id] = {}
                expense_map[ca_id][cr_id] = row
                resource_ids.append(resource_id)
            resources = self._get_resources_info(resource_ids,
                                                 start_date_resources)
            for resource in resources:
                expense_info = expense_map[resource['cloud_account_id']][
                    resource['cloud_resource_id']]
                hours = (expense_info['last_end'] - expense_info[
                    'last_start']).total_seconds() // 3600
                price = float(expense_info['price'])
                try:
                    capacity = int(expense_info['cost'] / hours / price)
                except ZeroDivisionError:
                    LOG.exception(
                        'Failed to calculate capacity for Amazon Kinesis Stream'
                        ' (cloud_account_id %s, cloud_resource_id %s):'
                        ' hours %s, price %s, expense_info %s',
                        resource['cloud_account_id'],
                        resource['cloud_resource_id'],
                        hours, price, expense_info)
                    raise
                shardhours_price = expense_info['cost'] / hours
                saving = capacity * price * 24 * 30
                ca_id = resource['cloud_account_id']
                if saving > 0:
                    result.append({
                        "cloud_resource_id": resource['cloud_resource_id'],
                        "resource_name": resource.get('name'),
                        "resource_id": resource['_id'],
                        "cloud_account_id": ca_id,
                        "cloud_type": cloud_accounts_map[ca_id]['type'],
                        "region": resource['region'],
                        "owner": self._extract_owner(
                            resource.get('employee_id'), employees),
                        "pool": self._extract_pool(
                            resource.get('pool_id'), pools),
                        'is_excluded': resource.get('pool_id') in excluded_pools,
                        "shardhours_capacity": capacity,
                        "shardhours_price": shardhours_price,
                        "saving": saving
                    })

        return result


def main(organization_id, config_client, created_at, **kwargs):
    return AbandonedKinesisStreams(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Abandoned Kinesis Streams'
