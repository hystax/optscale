import abc
import os

from cloud_adapter.clouds.aws import Aws
from cloud_adapter.clouds.aws_fake import AwsFake
from cloud_adapter.clouds.alibaba import Alibaba
from cloud_adapter.clouds.azure import Azure
from cloud_adapter.clouds.azure_fake import AzureFake
from cloud_adapter.clouds.kubernetes import Kubernetes
from cloud_adapter.clouds.environment import Environment
from cloud_adapter.clouds.gcp import Gcp


FAKE_SUPPORTED_BILLING_TYPES = {
    'aws_cnr': AwsFake,
    'azure_cnr': AzureFake
}


SUPPORTED_BILLING_TYPES = {
    'aws_cnr': Aws,
    'azure_cnr': Azure,
    'kubernetes_cnr': Kubernetes,
    'alibaba_cnr': Alibaba,
    'environment': Environment,
    'gcp_cnr': Gcp,
}


class Cloud(metaclass=abc.ABCMeta):

    __modules__ = FAKE_SUPPORTED_BILLING_TYPES if int(os.environ.get(
        'FAKE_CAD_ENABLED', 0)) else SUPPORTED_BILLING_TYPES

    @staticmethod
    def get_adapter(cloud_config):
        type_ = cloud_config.get('type').lower()
        if type_ in Cloud.__modules__:
            return Cloud.__modules__.get(type_)(cloud_config)
        raise ValueError('Cloud not supported')

    @staticmethod
    def get_adapter_type(cloud_type):
        if cloud_type in Cloud.__modules__:
            return Cloud.__modules__.get(cloud_type)
        raise ValueError('Cloud not supported')

