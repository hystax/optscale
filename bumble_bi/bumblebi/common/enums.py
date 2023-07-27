from enum import Enum, auto


class BITypes(str, Enum):
    AWS_REPORT_EXPORT = 'AWS_REPORT_EXPORT'
    AZURE_REPORT_EXPORT = 'AZURE_REPORT_EXPORT'


# copied from rest-api
class CloudTypes(Enum):
    AWS_CNR = 'aws_cnr'
    ALIBABA_CNR = 'alibaba_cnr'
    AZURE_CNR = 'azure_cnr'
    KUBERNETES_CNR = 'kubernetes_cnr'
    GCP_CNR = 'gcp_cnr'
    NEBIUS = 'nebius'
    ENVIRONMENT = 'environment'


class DataSetEnum(str, Enum):
    EXPENSES = 'expenses'
    RESOURCES = 'resources'
    RECOMMENDATIONS = 'recommendations'


class ColumnTypes(Enum):
    STRING = auto()
    INTEGER = auto()
    DECIMAL = auto()
    DATETIME = auto()
    BIT = auto()
    BOOLEAN = auto()
    JSON = auto()
