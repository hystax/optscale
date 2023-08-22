from bi_exporter.bumblebi.common.dataclasses import CsvColumn
from bi_exporter.bumblebi.common.enums import (CloudTypes, DataSetEnum,
                                               ColumnTypes)

# mapping of our internal names to human readable
CLOUD_NAME_MAP = {
    CloudTypes.AWS_CNR: "AWS",
    CloudTypes.ALIBABA_CNR: "Alibaba Cloud",
    CloudTypes.AZURE_CNR: "Azure",
    CloudTypes.KUBERNETES_CNR: "Kubernetes",
    CloudTypes.GCP_CNR: "GCP",
    CloudTypes.NEBIUS: "Nebius",
    CloudTypes.ENVIRONMENT: "Environment",
}

COLUMNS = {
    DataSetEnum.EXPENSES: [
        CsvColumn("Date", ColumnTypes.DATETIME),
        CsvColumn("Resource ID", ColumnTypes.STRING),
        CsvColumn("Cost", ColumnTypes.DECIMAL),
    ],
    DataSetEnum.RESOURCES: [
        CsvColumn("Organization Name"),
        CsvColumn("Organization ID"),
        CsvColumn("Cloud Account ID"),
        CsvColumn("Cloud"),
        CsvColumn("Cloud Account"),
        CsvColumn("Resource ID"),
        CsvColumn("Cloud Resource ID"),
        CsvColumn("Cloud Console Link"),
        CsvColumn("Employee ID"),
        CsvColumn("Owner Name"),
        CsvColumn("Tags"),
        CsvColumn("First Seen", ColumnTypes.DATETIME),
        CsvColumn("Last Seen", ColumnTypes.DATETIME),
        CsvColumn("Resource Name"),
        CsvColumn("Pool ID"),
        CsvColumn("Pool Name"),
        CsvColumn("Pool Purpose"),
        CsvColumn("Pool Parent"),
        CsvColumn("Region"),
        CsvColumn("Resource Type"),
        CsvColumn("Active"),
        CsvColumn("Cluster ID"),
        CsvColumn("Cluster Name"),
        CsvColumn("Service"),
    ],
    DataSetEnum.RECOMMENDATIONS: [
        CsvColumn("Resource ID"),
        CsvColumn("Module"),
        CsvColumn("Saving", ColumnTypes.DECIMAL),
    ]
}

HEADERS = {
    DataSetEnum.EXPENSES: [x.name for x in COLUMNS[DataSetEnum.EXPENSES]],
    DataSetEnum.RESOURCES: [x.name for x in COLUMNS[DataSetEnum.RESOURCES]],
    DataSetEnum.RECOMMENDATIONS: [x.name for x in COLUMNS[DataSetEnum.RECOMMENDATIONS]],
}
