import boto3
import re
import abc
import logging
import threading
from botocore.config import Config as CoreConfig
from botocore.loaders import create_loader
from botocore.session import Session as CoreSession
from tools.cloud_adapter.exceptions import (InvalidResourceTypeException,
                                            BucketPrefixValidationError)
from tools.cloud_adapter.model import RES_MODEL_MAP

DEFAULT_CLIENT_CONFIG = CoreConfig(
    connect_timeout=20, retries={'max_attempts': 3}
)

LOG = logging.getLogger(__name__)

_shared_data_loader = None
_shared_data_loader_lock = threading.Lock()


def _get_shared_data_loader():
    """A single, process-wide botocore Loader, reused as the `data_loader`
    component of every fresh CoreSession() we create, regardless of which
    cloud account it's for.

    botocore parses each service's API model (shapes, operations,
    paginators - EC2's is one of the largest) from JSON into Python
    objects and caches it on the Loader the first time a client for that
    service is created. A brand-new CoreSession() gets its own Loader and
    re-pays that parse cost from scratch (~15-20MB of RSS for EC2 alone,
    measured), even though the process already parsed the same model
    moments ago for a different account. Sharing just the Loader avoids
    paying that cost again on every single task, while still giving every
    caller its own CoreSession for credentials.

    The Loader holds no credentials or other per-account state - only a
    memorizing cache of parsed (service, type, api_version) -> model, so
    sharing it across concurrently-running tasks for different accounts
    is safe.
    """
    global _shared_data_loader
    if _shared_data_loader is None:
        with _shared_data_loader_lock:
            if _shared_data_loader is None:
                _shared_data_loader = create_loader()
    return _shared_data_loader


def new_core_session():
    """A fresh, per-caller botocore Session pre-loaded with the shared,
    process-wide data_loader (see `_get_shared_data_loader`) so it doesn't
    re-parse service API models that another task already parsed.

    Unlike a single shared CoreSession, this keeps credentials and other
    session state (region, etc.) fully isolated per caller: safe to use
    even when multiple threads are building clients for different cloud
    accounts at the same time (e.g. diworker's concurrent report imports).
    """
    session = CoreSession()
    session.register_component('data_loader', _get_shared_data_loader())
    session.set_default_client_config(DEFAULT_CLIENT_CONFIG)
    return session


class CloudBase(abc.ABC):
    @abc.abstractmethod
    def discovery_calls_map(self):
        raise NotImplementedError

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

    @abc.abstractmethod
    def validate_credentials(self, org_id=None):
        raise NotImplementedError

    @abc.abstractmethod
    def configure_report(self):
        raise NotImplementedError

    @abc.abstractmethod
    def set_currency(self, currency):
        raise NotImplementedError

    @abc.abstractmethod
    def get_regions_coordinates(self, load=True):
        raise NotImplementedError

    def close(self):
        pass


class S3CloudMixin(CloudBase):
    DEFAULT_S3_REGION_NAME = None
    S3_ENDPOINT = None

    SUPPORTS_REPORT_UPLOAD = True

    def __init__(self, cloud_config, *args, **kwargs):
        self.config = cloud_config
        self._session = None

    def get_session(self, access_key_id=None, secret_access_key=None,
                    region_name=None):
        if not access_key_id:
            access_key_id = self.config.get('access_key_id')
        if not secret_access_key:
            secret_access_key = self.config.get('secret_access_key')
        return boto3.Session(
            region_name=region_name or self.DEFAULT_S3_REGION_NAME,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            botocore_session=new_core_session(),
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
