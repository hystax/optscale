import logging
from collections import defaultdict
from datetime import datetime, timedelta

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.abandoned_kinesis_streams import (
    AbandonedKinesisStreams as AbandonedKinesisStreamsRecommendation,
    SUPPORTED_CLOUD_TYPES)


LOG = logging.getLogger(__name__)


class AbandonedKinesisStreams(ArchiveBase,
                              AbandonedKinesisStreamsRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'kinesis stream deleted')
        self.reason_description_map[ArchiveReason.RECOMMENDATION_IRRELEVANT] = (
            'got extra operations')
        self.reason_description_map[ArchiveReason.FAILED_DEPENDENCY] = (
            'pricing model changed')

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get_expenses(self, cloud_account_id, cloud_resource_ids, start_date):
        pipeline = [
            {
                '$match':
                    {
                        'cloud_account_id': cloud_account_id,
                        'resource_id': {'$in': cloud_resource_ids},
                        'start_date': {'$gte': start_date},
                        'product/servicecode': 'AmazonKinesis',
                        'pricing/term': {'$exists': True}
                    }
            },
            {
                '$sort': {'end_date': -1}
            },
            {
                '$group':
                    {
                        '_id': '$resource_id',
                        'operation': {'$addToSet': '$lineItem/Operation'},
                        'pricing': {'$addToSet': '$pricing/term'},
                        'last_end': {'$first': '$end_date'}
                    }
            }
        ]
        return self.mongo_client.restapi.raw_expenses.aggregate(pipeline)

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        days_threshold = previous_options['days_threshold']

        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)

        result = []
        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            cloud_resource_ids = list(
                map(lambda x: x['cloud_resource_id'], optimizations_))
            last_import = datetime.fromtimestamp(
                cloud_accounts_map[cloud_account_id][
                    'last_import_at']).replace(hour=0, minute=0, second=0,
                                               microsecond=0)
            active_date = self.get_active_date(last_import)
            start_date_raw_expenses = self.get_start_date_raw_expenses(
                last_import, days_threshold)
            expenses = self._get_expenses(
                cloud_account_id, cloud_resource_ids, start_date_raw_expenses)
            expenses_map = {x['_id']: x for x in expenses}
            for optimization in optimizations_:
                cloud_resource_id = optimization['cloud_resource_id']
                resource = expenses_map.get(cloud_resource_id)
                if not resource or resource['last_end'] < active_date:
                    reason = ArchiveReason.RECOMMENDATION_APPLIED
                elif resource['pricing'] != ['OnDemand']:
                    reason = ArchiveReason.FAILED_DEPENDENCY
                elif resource['operation'] != ['shardHourStorage']:
                    reason = ArchiveReason.RECOMMENDATION_IRRELEVANT
                else:
                    reason = ArchiveReason.OPTIONS_CHANGED
                self._set_reason_properties(optimization, reason)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return AbandonedKinesisStreams(
        organization_id, config_client, created_at).get()
