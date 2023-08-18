from diworker.diworker.importers.aws import AWSReportImporter
from diworker.diworker.importers.azure import AzureReportImporter
from diworker.diworker.importers.kubernetes import KubernetesReportImporter
from diworker.diworker.importers.alibaba import AlibabaReportImporter
from diworker.diworker.importers.gcp import GcpReportImporter
from diworker.diworker.importers.nebius import NebiusReportImporter
from diworker.diworker.importers.environment import EnvironmentReportImporter

REPORT_IMPORTER_TYPES = {
    'aws_cnr': AWSReportImporter,
    'azure_cnr': AzureReportImporter,
    'kubernetes_cnr': KubernetesReportImporter,
    'alibaba_cnr': AlibabaReportImporter,
    'gcp_cnr': GcpReportImporter,
    'nebius': NebiusReportImporter,
    'environment': EnvironmentReportImporter
}


def get_importer_class(cloud_type):
    if cloud_type not in REPORT_IMPORTER_TYPES:
        raise ValueError('Cloud {} is not supported'.format(cloud_type))
    return REPORT_IMPORTER_TYPES[cloud_type]
