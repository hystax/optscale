from bumiworker.bumiworker.modules.abandoned_base import (
    S3AbandonedBucketsArchiveBase
)
from bumiworker.bumiworker.modules.recommendations.s3_abandoned_buckets import (
    S3AbandonedBuckets as S3AbandonedBucketsRecommendation,
    AVG_DATA_SIZE_KEY, TIER_1_REQUESTS_QUANTITY_KEY,
    TIER_2_REQUESTS_QUANTITY_KEY
)


class S3AbandonedBuckets(S3AbandonedBucketsArchiveBase,
                         S3AbandonedBucketsRecommendation):
    SUPPORTED_CLOUD_TYPES = [
        'aws_cnr'
    ]

    def get_previous_metric_threshold_map(self, previous_options):
        return {
            TIER_1_REQUESTS_QUANTITY_KEY: previous_options.get(
                'tier_1_request_quantity_threshold'),
            TIER_2_REQUESTS_QUANTITY_KEY: previous_options.get(
                'tier_2_request_quantity_threshold'),
            AVG_DATA_SIZE_KEY: previous_options.get('data_size_threshold')
        }


def main(organization_id, config_client, created_at, **kwargs):
    return S3AbandonedBuckets(
        organization_id, config_client, created_at).get()
