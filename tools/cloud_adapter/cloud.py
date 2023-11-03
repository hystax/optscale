import abc

from tools.cloud_adapter.clouds.aws import Aws
from tools.cloud_adapter.clouds.alibaba import Alibaba
from tools.cloud_adapter.clouds.azure import Azure
from tools.cloud_adapter.clouds.azure_tenant import AzureTenant
from tools.cloud_adapter.clouds.kubernetes import Kubernetes
from tools.cloud_adapter.clouds.environment import Environment
from tools.cloud_adapter.clouds.gcp import Gcp
from tools.cloud_adapter.clouds.nebius import Nebius
from tools.cloud_adapter.clouds.databricks import Databricks


SUPPORTED_BILLING_TYPES = {
    'aws_cnr': Aws,
    'azure_cnr': Azure,
    'azure_tenant': AzureTenant,
    'kubernetes_cnr': Kubernetes,
    'alibaba_cnr': Alibaba,
    'environment': Environment,
    'gcp_cnr': Gcp,
    'nebius': Nebius,
    'databricks': Databricks
}


class Cloud(metaclass=abc.ABCMeta):

    __modules__ = SUPPORTED_BILLING_TYPES

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
