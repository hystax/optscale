from enum import Enum


class CloudTypes(Enum):
    AWS_CNR = 'aws_cnr'
    ALIBABA_CNR = 'alibaba_cnr'
    AZURE_CNR = 'azure_cnr'
    AZURE_TENANT = 'azure_tenant'
    KUBERNETES_CNR = 'kubernetes_cnr'
    GCP_CNR = 'gcp_cnr'
    GCP_TENANT = 'gcp_tenant'
    NEBIUS = 'nebius'
    ENVIRONMENT = 'environment'
    DATABRICKS = 'databricks'
    FOCUS = 'focus'
