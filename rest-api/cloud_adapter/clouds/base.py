import boto3
import re
from botocore.config import Config as CoreConfig
from botocore.session import Session as CoreSession
from cloud_adapter.exceptions import (InvalidResourceTypeException,
                                      BucketPrefixValidationError)
from cloud_adapter.model import RES_MODEL_MAP

DEFAULT_CLIENT_CONFIG = CoreConfig(
    connect_timeout=20, retries={'max_attempts': 3}
)


class CloudBase:
    def discovery_calls_map(self):
        return {}

    def get_discovery_calls(self, resource_type):
        try:
            resource = RES_MODEL_MAP[resource_type]
        except KeyError:
            raise InvalidResourceTypeException(
                'Invalid resource type %s' % resource_type)
        func = self.discovery_calls_map().get(resource)
        if func:
            return func()
        else:
            return []

    @classmethod
    def configure_credentials(cls, config):
        return config

    def get_children_configs(self):
        return []


class S3CloudMixin(CloudBase):
    DEFAULT_S3_REGION_NAME = None
    S3_ENDPOINT = None

    SUPPORTS_REPORT_UPLOAD = True

    def __init__(self, cloud_config, *args, **kwargs):
        self.config = cloud_config
        self._session = None

    def get_session(self, access_key_id=None, secret_access_key=None,
                    region_name=None):
        core_session = CoreSession()
        core_session.set_default_client_config(DEFAULT_CLIENT_CONFIG)
        if not access_key_id:
            access_key_id = self.config.get('access_key_id')
        if not secret_access_key:
            secret_access_key = self.config.get('secret_access_key')
        return boto3.Session(
            region_name=region_name or self.DEFAULT_S3_REGION_NAME,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            botocore_session=core_session,
        )

    @property
    def session(self):
        if self._session is None:
            self._session = self.get_session(
                self.config.get('access_key_id'),
                self.config.get('secret_access_key'),
                self.config.get('region_name', self.DEFAULT_S3_REGION_NAME))
        return self._session

    @property
    def s3(self):
        kwargs = {}
        s3_endpoint = self.config.get('s3_endpoint', self.S3_ENDPOINT)
        if s3_endpoint:
            kwargs['endpoint_url'] = s3_endpoint
        region = self.config.get('region_name', self.DEFAULT_S3_REGION_NAME)
        if region:
            kwargs['region_name'] = region
        return self.session.client('s3', **kwargs)

    @staticmethod
    def is_valid_s3_object_key(object_key):
        # Added pattern according to s3 object name
        regex_pattern = '^[a-zA-Z0-9!_.*\'()-\\\\/|]+$'
        return re.match(regex_pattern, object_key) is not None

    def check_prefix_report_name(self, prefix):
        if prefix and not self.is_valid_s3_object_key(prefix):
            raise BucketPrefixValidationError('Bucket prefix "{}" has incorrect'
                                              ' format'.format(prefix))
