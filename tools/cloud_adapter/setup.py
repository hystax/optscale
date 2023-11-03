#!/usr/bin/env python
from setuptools import setup

requirements = [
    # AWS
    'boto3==1.18.9',

    # Alibaba Cloud
    'aliyun-python-sdk-ecs==4.24.1',
    'aliyun-python-sdk-core-v3==2.13.32',
    'aliyun-python-sdk-ram==3.2.0',
    'aliyun-python-sdk-sts==3.0.2',
    'aliyun-python-sdk-bssopenapi==1.6.8',
    'aliyun-python-sdk-cms==7.0.22',
    'aliyun-python-sdk-rds==2.5.11',
    'aliyun-python-sdk-vpc==3.0.14',

    # Azure
    'azure-mgmt-resource==2.1.0',
    'azure-mgmt-network==2.6.0',
    'azure-mgmt-compute==7.0.0',
    "azure-storage-blob==1.5.0",
    'azure-mgmt-storage==3.3.0',
    "azure_mgmt_subscription==0.2.0",
    "azure-mgmt-consumption==8.0.0",
    "azure-mgmt-monitor==0.10.0",
    "azure-mgmt-commerce==1.0.1",
    "msrest==0.6.6",
    "urllib3==1.26.18",
    "azure-identity==1.6.1",

    # Gcp
    'google-cloud-bigquery==3.11.4',
    'google-cloud-compute==1.14.1',
    'google-cloud-storage==2.10.0',
    'google-cloud-monitoring==2.15.1',

    # Nebius
    'yandexcloud==0.191.0',

    # Databricks
    'databricks-sdk==0.11.0',

    "requests==2.31.0",
    "retrying==1.3.3",
]

setup(name='cloud-adapter',
      description='OptScale Cloud adapter',
      url='http://hystax.com',
      author='Hystax',
      author_email='info@hystax.com',
      package_dir={'cloud_adapter': ''},
      packages=['cloud_adapter', 'cloud_adapter.clouds', 'cloud_adapter.lib',
                'cloud_adapter.lib.azure_partner'],
      install_requires=requirements,
      )
