import logging

from datetime import datetime
from tools.cloud_adapter.cloud import Cloud
from gemini.gemini_worker.duplicate_object_finder.aws.object_info import ObjectInfo

LOG = logging.getLogger(__file__)


class DefaultAWSClientFactory:
    def __init__(
        self,
        config=None,
    ):
        self._config = config
        self.cloud_adapter = Cloud.get_adapter(self._config)

    def create_client(self):
        return self.cloud_adapter.s3


class AWSObjectEnumerator:
    def __init__(
        self, buckets: set[str], stats, client_factory: DefaultAWSClientFactory
    ):
        self.buckets = buckets
        self._stats = stats
        self._client_factory = client_factory

    def enumerate(self):
        s3 = self._client_factory.create_client()
        for bucket in self.buckets:
            bucket_start = datetime.now()
            LOG.info(
                f"Started processing of bucket {bucket} at {bucket_start}")
            try:
                response = s3.get_bucket_location(Bucket=bucket)
            except s3.exceptions.NoSuchBucket:
                # TODO: think about retry
                LOG.exception(f"Bucket {bucket} doesn't exist")
                continue

            # Buckets in region us-east-1 have a LocationConstraint of None
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_bucket_location.html

            location_constraint = response.get("LocationConstraint")

            if not location_constraint:
                # LocationConstraint will be None if bucket is located in us-east-1
                region = 'us-east-1'
            elif location_constraint.lower() == 'eu':
                # LocationConstraint will be EU if bucket is located in eu-west-1
                region = 'eu-west-1'
            else:
                region = location_constraint
                LOG.info(f"Processing bucket {bucket} in {region}")

            paginator = self._client_factory.create_client().get_paginator(
                "list_objects_v2")

            kwargs = {"Bucket": bucket}
            before_request = datetime.now()

            for num, page in enumerate(paginator.paginate(**kwargs)):
                self._stats.timedelta_requests += datetime.now() - before_request
                try:
                    contents = page["Contents"]
                except KeyError:
                    LOG.exception(f"No data on page {num}")
                    continue
                yield [ObjectInfo.from_aws_object_info(bucket, obj) for obj in contents]
                before_request = datetime.now()

            bucket_finish = datetime.now()
            LOG.info(
                f"Finished processing of bucket {bucket} at {bucket_finish}")
            LOG.info(
                f"Time spent for processing of bucket {bucket} is {bucket_finish - bucket_start}"
            )
