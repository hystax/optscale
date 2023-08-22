from bi_exporter.bumblebi.exporter.exporter import (
    BaseExporter, AwsExporter, AzureExporter)
from optscale_client.config_client.client import Client as ConfigClient


class ExporterFactory:
    @staticmethod
    def get(type_: str, config_cl: ConfigClient, credentials: dict) -> BaseExporter:
        if type_ == "AWS_RAW_EXPORT":
            return AwsExporter(config_cl, credentials)
        elif type_ == "AZURE_RAW_EXPORT":
            return AzureExporter(config_cl, credentials)
        raise Exception(f"Unknown BI type: {type_}")
