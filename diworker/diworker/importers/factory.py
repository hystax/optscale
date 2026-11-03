from diworker.diworker.importers.aws import AWSReportImporter
from diworker.diworker.importers.azure import AzureApiImporter
from diworker.diworker.importers.azure_export import AzureExportImporter
from diworker.diworker.importers.kubernetes import KubernetesReportImporter
from diworker.diworker.importers.alibaba import AlibabaReportImporter
from diworker.diworker.importers.gcp import GcpReportImporter
from diworker.diworker.importers.nebius import NebiusReportImporter
from diworker.diworker.importers.environment import EnvironmentReportImporter
from diworker.diworker.importers.databricks import DatabricksReportImporter
from diworker.diworker.importers.focus import FocusReportImporter

REPORT_IMPORTER_TYPES = {
    ('aws_cnr', None): AWSReportImporter,
    ('azure_cnr', None): AzureApiImporter,
    ('azure_cnr', 'usage'): AzureApiImporter,
    ('azure_cnr', 'raw_usage'): AzureApiImporter,
    ('azure_cnr', 'partner_raw_usage'): AzureApiImporter,
    ('azure_cnr', 'export'): AzureExportImporter,
    ('kubernetes_cnr', None): KubernetesReportImporter,
    ('alibaba_cnr', None): AlibabaReportImporter,
    ('gcp_cnr', None): GcpReportImporter,
    ('nebius', None): NebiusReportImporter,
    ('environment', None): EnvironmentReportImporter,
    ('databricks', None): DatabricksReportImporter,
    ('focus', None): FocusReportImporter
}


def get_importer_class(cloud_type, import_scheme):
    cloud_types = [x[0] for x in REPORT_IMPORTER_TYPES]
    if cloud_type not in cloud_types:
        raise ValueError('Cloud {} is not supported'.format(cloud_type))
    import_schemes = [x[1] for x in REPORT_IMPORTER_TYPES]
    if import_scheme not in import_schemes:
        raise ValueError('Expense import scheme {} is not supported'.format(
            import_scheme))
    return REPORT_IMPORTER_TYPES[(cloud_type, import_scheme)]
