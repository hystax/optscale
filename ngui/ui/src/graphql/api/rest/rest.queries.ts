import { gql } from "@apollo/client";

const GET_DATA_SOURCE = gql`
  query DataSource($dataSourceId: ID!, $requestParams: DataSourceRequestParams) {
    dataSource(dataSourceId: $dataSourceId, requestParams: $requestParams) {
      account_id
      id
      last_getting_metric_attempt_at
      last_getting_metric_attempt_error
      last_getting_metrics_at
      last_import_at
      last_import_attempt_at
      last_import_attempt_error
      name
      parent_id
      type
      details {
        cost
        discovery_infos {
          cloud_account_id
          created_at
          deleted_at
          enabled
          id
          last_discovery_at
          last_error
          last_error_at
          observe_time
          resource_type
        }
        forecast
        last_month_cost
        resources
      }
      ... on AwsDataSource {
        config {
          access_key_id
          linked
          bucket_name
          bucket_prefix
          config_scheme
          region_name
          report_name
        }
      }
      ... on AzureTenantDataSource {
        config {
          client_id
          tenant
        }
      }
      ... on AzureSubscriptionDataSource {
        config {
          client_id
          expense_import_scheme
          subscription_id
          tenant
        }
      }
      ... on GcpDataSource {
        config {
          billing_data {
            dataset_name
            table_name
            project_id
          }
        }
      }
      ... on AlibabaDataSource {
        config {
          access_key_id
        }
      }
      ... on NebiusDataSource {
        config {
          cloud_name
          service_account_id
          key_id
          access_key_id
          bucket_name
          bucket_prefix
        }
      }
      ... on DatabricksDataSource {
        config {
          account_id
          client_id
        }
      }
      ... on K8sDataSource {
        config {
          cost_model {
            cpu_hourly_cost
            memory_hourly_cost
          }
          user
        }
      }
    }
  }
`;

export { GET_DATA_SOURCE };
