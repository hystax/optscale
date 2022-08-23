from enum import Enum


class CloudTypes(Enum):
    AWS_CNR = 'aws_cnr'
    ALIBABA_CNR = 'alibaba_cnr'
    AZURE_CNR = 'azure_cnr'
    KUBERNETES_CNR = 'kubernetes_cnr'
    ENVIRONMENT = 'environment'
