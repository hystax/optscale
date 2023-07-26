import React from "react";
import DataSourceDetails from "components/DataSourceDetails";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/DataSourceDetails`
};

export const awsDataSourceDetails = () => (
  <DataSourceDetails
    id="01234567-f0ee-4445-8069-bc125b928fd6"
    accountId="123456789101"
    type="aws_cnr"
    config={{
      bucket_name: "report-bucket",
      bucket_prefix: "reports",
      report_name: "report",
      access_key_id: "ABCDEFGHIJKLMNOPQRT"
    }}
  />
);

export const azureDataSourceDetails = () => (
  <DataSourceDetails
    id="01234567-f0ee-4445-8069-bc125b928fd6"
    accountId="01234567-0d60-4c01-adce-b6269d527407"
    type="azure_cnr"
    config={{
      subscription_id: "01234567-0d60-4c01-adce-b6269d527407",
      client_id: "01234567-fc44-44b1-8725-59196f91e1b9",
      tenant: "01234567-dc92-4770-bc5a-18d7005efe29",
      expense_import_scheme: "raw_usage"
    }}
  />
);

export const kubernetesDataSourceDetails = () => (
  <DataSourceDetails
    id="01234567-85be-4e00-9ffc-401292bb6f9f"
    accountId="01234567-09f2-45ea-b4df-c56d854cda86"
    type="kubernetes_cnr"
    config={{
      user: "optscale",
      cost_model: {
        cpu_hourly_cost: 0.002,
        memory_hourly_cost: 0.001
      }
    }}
  />
);

export const alibabaDataSourceDetails = () => (
  <DataSourceDetails
    id="01234567-ca28-42e8-8b43-390aeaa3ad94"
    accountId="1237456789101112"
    type="alibaba_cnr"
    config={{
      access_key_id: "ABCDEfGhijKlMNO1PUK5Yvg4"
    }}
  />
);

export const googleCloudDataSourceDetails = () => (
  <DataSourceDetails
    id="01234567-e4d3-4a04-8781-4d7262b585fc"
    accountId="optscale"
    type="gcp_cnr"
    config={{
      billing_data: {
        dataset_name: "billing_data",
        table_name: "gcp_billing_export_version"
      }
    }}
  />
);
