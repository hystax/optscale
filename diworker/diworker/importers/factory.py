from diworker.importers.aws import AWSReportImporter
from diworker.importers.azure import AzureReportImporter
from diworker.importers.kubernetes import KubernetesReportImporter
from diworker.importers.alibaba import AlibabaReportImporter
from diworker.importers.gcp import GcpReportImporter
from diworker.importers.nebius import NebiusReportImporter
from diworker.importers.environment import EnvironmentReportImporter

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
