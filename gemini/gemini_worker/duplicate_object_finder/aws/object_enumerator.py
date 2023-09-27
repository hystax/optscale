import logging
import boto3

from datetime import datetime
from gemini.gemini_worker.duplicate_object_finder.aws.object_info import ObjectInfo

LOG = logging.getLogger(__file__)


class DefaultAWSClientFactory:
    def __init__(
        self,
        endpoint_url=None,
        access_key_id=None,
        secret_access_key=None,
        config=None,
    ):
        self._endpoint_url = endpoint_url
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self._config = config

    def create_client(self, region=None):
        return boto3.client(
            "s3",
            endpoint_url=self._endpoint_url,
            region_name=region,
            aws_access_key_id=self._access_key_id,
            aws_secret_access_key=self._secret_access_key,
            config=self._config,
        )


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
            region = response.get("LocationConstraint") or "us-east-1"
            LOG.info(f"Processing bucket {bucket} in {region}")

            paginator = self._client_factory.create_client(
                region).get_paginator("list_objects_v2")

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
