import { gql } from "@apollo/client";
import * as Apollo from "@apollo/client";
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends " $fragmentName" | "__typename" ? T[P] : never };
const defaultOptions = {} as const;
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string };
  String: { input: string; output: string };
  Boolean: { input: boolean; output: boolean };
  Int: { input: number; output: number };
  Float: { input: number; output: number };
  JSONObject: { input: Record<string, unknown>; output: Record<string, unknown> };
};

export type AlibabaConfig = {
  __typename?: "AlibabaConfig";
  access_key_id?: Maybe<Scalars["String"]["output"]>;
};

export type AlibabaConfigInput = {
  access_key_id: Scalars["String"]["input"];
  secret_access_key: Scalars["String"]["input"];
};

export type AlibabaDataSource = DataSourceInterface & {
  __typename?: "AlibabaDataSource";
  account_id: Scalars["String"]["output"];
  config?: Maybe<AlibabaConfig>;
  created_at?: Maybe<Scalars["Int"]["output"]>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars["String"]["output"];
  last_getting_metric_attempt_at: Scalars["Int"]["output"];
  last_getting_metric_attempt_error?: Maybe<Scalars["String"]["output"]>;
  last_getting_metrics_at: Scalars["Int"]["output"];
  last_import_at: Scalars["Int"]["output"];
  last_import_attempt_at: Scalars["Int"]["output"];
  last_import_attempt_error?: Maybe<Scalars["String"]["output"]>;
  name: Scalars["String"]["output"];
  parent_id?: Maybe<Scalars["String"]["output"]>;
  type: DataSourceType;
};

export type AvailableFiltersParams = {
  active?: InputMaybe<Array<Scalars["Boolean"]["input"]>>;
  cloud_account_id?: InputMaybe<Array<Scalars["String"]["input"]>>;
  constraint_violated?: InputMaybe<Array<Scalars["Boolean"]["input"]>>;
  end_date: Scalars["Int"]["input"];
  first_seen_gte?: InputMaybe<Scalars["Int"]["input"]>;
  first_seen_lte?: InputMaybe<Scalars["Int"]["input"]>;
  k8s_namespace?: InputMaybe<Array<Scalars["String"]["input"]>>;
  k8s_node?: InputMaybe<Array<Scalars["String"]["input"]>>;
  k8s_service?: InputMaybe<Array<Scalars["String"]["input"]>>;
  last_seen_gte?: InputMaybe<Scalars["Int"]["input"]>;
  last_seen_lte?: InputMaybe<Scalars["Int"]["input"]>;
  meta?: InputMaybe<Array<Scalars["String"]["input"]>>;
  owner_id?: InputMaybe<Array<Scalars["String"]["input"]>>;
  pool_id?: InputMaybe<Array<Scalars["String"]["input"]>>;
  recommendations?: InputMaybe<Array<Scalars["Boolean"]["input"]>>;
  region?: InputMaybe<Array<Scalars["String"]["input"]>>;
  resource_type?: InputMaybe<Array<Scalars["String"]["input"]>>;
  service_name?: InputMaybe<Array<Scalars["String"]["input"]>>;
  start_date: Scalars["Int"]["input"];
  tag?: InputMaybe<Array<Scalars["String"]["input"]>>;
  traffic_from?: InputMaybe<Array<Scalars["String"]["input"]>>;
  traffic_to?: InputMaybe<Array<Scalars["String"]["input"]>>;
  without_tag?: InputMaybe<Array<Scalars["String"]["input"]>>;
};

export type AwsAssumedRoleConfigInput = {
  assume_role_account_id: Scalars["String"]["input"];
  assume_role_name: Scalars["String"]["input"];
  bucket_name?: InputMaybe<Scalars["String"]["input"]>;
  bucket_prefix?: InputMaybe<Scalars["String"]["input"]>;
  config_scheme?: InputMaybe<Scalars["String"]["input"]>;
  cur_version?: InputMaybe<Scalars["Int"]["input"]>;
  region_name?: InputMaybe<Scalars["String"]["input"]>;
  report_name?: InputMaybe<Scalars["String"]["input"]>;
  use_edp_discount?: InputMaybe<Scalars["Boolean"]["input"]>;
};

export type AwsConfig = {
  __typename?: "AwsConfig";
  access_key_id?: Maybe<Scalars["String"]["output"]>;
  assume_role_account_id?: Maybe<Scalars["String"]["output"]>;
  assume_role_name?: Maybe<Scalars["String"]["output"]>;
  bucket_name?: Maybe<Scalars["String"]["output"]>;
  bucket_prefix?: Maybe<Scalars["String"]["output"]>;
  config_scheme?: Maybe<Scalars["String"]["output"]>;
  cur_version?: Maybe<Scalars["Int"]["output"]>;
  linked?: Maybe<Scalars["Boolean"]["output"]>;
  region_name?: Maybe<Scalars["String"]["output"]>;
  report_name?: Maybe<Scalars["String"]["output"]>;
  use_edp_discount?: Maybe<Scalars["Boolean"]["output"]>;
};

export type AwsDataSource = DataSourceInterface & {
  __typename?: "AwsDataSource";
  account_id: Scalars["String"]["output"];
  config?: Maybe<AwsConfig>;
  created_at?: Maybe<Scalars["Int"]["output"]>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars["String"]["output"];
  last_getting_metric_attempt_at: Scalars["Int"]["output"];
  last_getting_metric_attempt_error?: Maybe<Scalars["String"]["output"]>;
  last_getting_metrics_at: Scalars["Int"]["output"];
  last_import_at: Scalars["Int"]["output"];
  last_import_attempt_at: Scalars["Int"]["output"];
  last_import_attempt_error?: Maybe<Scalars["String"]["output"]>;
  name: Scalars["String"]["output"];
  parent_id?: Maybe<Scalars["String"]["output"]>;
  type: DataSourceType;
};

export type AwsLinkedConfigInput = {
  access_key_id: Scalars["String"]["input"];
  linked: Scalars["Boolean"]["input"];
  secret_access_key: Scalars["String"]["input"];
};

export type AwsRootConfigInput = {
  access_key_id: Scalars["String"]["input"];
  bucket_name?: InputMaybe<Scalars["String"]["input"]>;
  bucket_prefix?: InputMaybe<Scalars["String"]["input"]>;
  config_scheme?: InputMaybe<Scalars["String"]["input"]>;
  cur_version?: InputMaybe<Scalars["Int"]["input"]>;
  region_name?: InputMaybe<Scalars["String"]["input"]>;
  report_name?: InputMaybe<Scalars["String"]["input"]>;
  secret_access_key: Scalars["String"]["input"];
  use_edp_discount?: InputMaybe<Scalars["Boolean"]["input"]>;
};

export type AzureSubscriptionConfig = {
  __typename?: "AzureSubscriptionConfig";
  client_id?: Maybe<Scalars["String"]["output"]>;
  container?: Maybe<Scalars["String"]["output"]>;
  directory?: Maybe<Scalars["String"]["output"]>;
  expense_import_scheme?: Maybe<Scalars["String"]["output"]>;
  export_name?: Maybe<Scalars["String"]["output"]>;
  subscription_id?: Maybe<Scalars["String"]["output"]>;
  tenant?: Maybe<Scalars["String"]["output"]>;
};

export type AzureSubscriptionConfigInput = {
  client_id: Scalars["String"]["input"];
  container?: InputMaybe<Scalars["String"]["input"]>;
  directory?: InputMaybe<Scalars["String"]["input"]>;
  export_name?: InputMaybe<Scalars["String"]["input"]>;
  sa_connection_string?: InputMaybe<Scalars["String"]["input"]>;
  secret: Scalars["String"]["input"];
  subscription_id: Scalars["String"]["input"];
  tenant: Scalars["String"]["input"];
};

export type AzureSubscriptionDataSource = DataSourceInterface & {
  __typename?: "AzureSubscriptionDataSource";
  account_id: Scalars["String"]["output"];
  config?: Maybe<AzureSubscriptionConfig>;
  created_at?: Maybe<Scalars["Int"]["output"]>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars["String"]["output"];
  last_getting_metric_attempt_at: Scalars["Int"]["output"];
  last_getting_metric_attempt_error?: Maybe<Scalars["String"]["output"]>;
  last_getting_metrics_at: Scalars["Int"]["output"];
  last_import_at: Scalars["Int"]["output"];
  last_import_attempt_at: Scalars["Int"]["output"];
  last_import_attempt_error?: Maybe<Scalars["String"]["output"]>;
  name: Scalars["String"]["output"];
  parent_id?: Maybe<Scalars["String"]["output"]>;
  type: DataSourceType;
};

export type AzureTenantConfig = {
  __typename?: "AzureTenantConfig";
  client_id?: Maybe<Scalars["String"]["output"]>;
  tenant?: Maybe<Scalars["String"]["output"]>;
};

export type AzureTenantConfigInput = {
  client_id: Scalars["String"]["input"];
  secret: Scalars["String"]["input"];
  tenant: Scalars["String"]["input"];
};

export type AzureTenantDataSource = DataSourceInterface & {
  __typename?: "AzureTenantDataSource";
  account_id: Scalars["String"]["output"];
  config?: Maybe<AzureTenantConfig>;
  created_at?: Maybe<Scalars["Int"]["output"]>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars["String"]["output"];
  last_getting_metric_attempt_at: Scalars["Int"]["output"];
  last_getting_metric_attempt_error?: Maybe<Scalars["String"]["output"]>;
  last_getting_metrics_at: Scalars["Int"]["output"];
  last_import_at: Scalars["Int"]["output"];
  last_import_attempt_at: Scalars["Int"]["output"];
  last_import_attempt_error?: Maybe<Scalars["String"]["output"]>;
  name: Scalars["String"]["output"];
  parent_id?: Maybe<Scalars["String"]["output"]>;
  type: DataSourceType;
};

export type BreakdownBy =
  | "cloud_account_id"
  | "employee_id"
  | "k8s_namespace"
  | "k8s_node"
  | "k8s_service"
  | "pool_id"
  | "region"
  | "resource_type"
  | "service_name";

export type BreakdownParams = {
  active?: InputMaybe<Array<Scalars["Boolean"]["input"]>>;
  breakdown_by: Scalars["String"]["input"];
  cloud_account_id?: InputMaybe<Array<Scalars["String"]["input"]>>;
  constraint_violated?: InputMaybe<Array<Scalars["Boolean"]["input"]>>;
  end_date: Scalars["Int"]["input"];
  first_seen_gte?: InputMaybe<Scalars["Int"]["input"]>;
  first_seen_lte?: InputMaybe<Scalars["Int"]["input"]>;
  k8s_namespace?: InputMaybe<Array<Scalars["String"]["input"]>>;
  k8s_node?: InputMaybe<Array<Scalars["String"]["input"]>>;
  k8s_service?: InputMaybe<Array<Scalars["String"]["input"]>>;
  last_seen_gte?: InputMaybe<Scalars["Int"]["input"]>;
  last_seen_lte?: InputMaybe<Scalars["Int"]["input"]>;
  meta?: InputMaybe<Array<Scalars["String"]["input"]>>;
  owner_id?: InputMaybe<Array<Scalars["String"]["input"]>>;
  pool_id?: InputMaybe<Array<Scalars["String"]["input"]>>;
  recommendations?: InputMaybe<Array<Scalars["Boolean"]["input"]>>;
  region?: InputMaybe<Array<Scalars["String"]["input"]>>;
  resource_type?: InputMaybe<Array<Scalars["String"]["input"]>>;
  service_name?: InputMaybe<Array<Scalars["String"]["input"]>>;
  start_date: Scalars["Int"]["input"];
  tag?: InputMaybe<Array<Scalars["String"]["input"]>>;
  traffic_from?: InputMaybe<Array<Scalars["String"]["input"]>>;
  traffic_to?: InputMaybe<Array<Scalars["String"]["input"]>>;
  without_tag?: InputMaybe<Array<Scalars["String"]["input"]>>;
};

export type CleanExpensesParams = {
  active?: InputMaybe<Array<InputMaybe<Scalars["Boolean"]["input"]>>>;
  cloud_account_id?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  constraint_violated?: InputMaybe<Array<InputMaybe<Scalars["Boolean"]["input"]>>>;
  end_date: Scalars["Int"]["input"];
  first_seen_gte?: InputMaybe<Scalars["Int"]["input"]>;
  first_seen_lte?: InputMaybe<Scalars["Int"]["input"]>;
  format?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  k8s_namespace?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  k8s_node?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  k8s_service?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  last_seen_gte?: InputMaybe<Scalars["Int"]["input"]>;
  last_seen_lte?: InputMaybe<Scalars["Int"]["input"]>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  meta?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  owner_id?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  pool_id?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  recommendations?: InputMaybe<Array<InputMaybe<Scalars["Boolean"]["input"]>>>;
  region?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  resource_type?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  service_name?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  start_date: Scalars["Int"]["input"];
  tag?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  traffic_from?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  traffic_to?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
  without_tag?: InputMaybe<Array<InputMaybe<Scalars["String"]["input"]>>>;
};

export type CloudPoliciesParams = {
  bucket_name: Scalars["String"]["input"];
  cloud_type: Scalars["String"]["input"];
};

export type CreateDataSourceInput = {
  alibabaConfig?: InputMaybe<AlibabaConfigInput>;
  awsAssumedRoleConfig?: InputMaybe<AwsAssumedRoleConfigInput>;
  awsLinkedConfig?: InputMaybe<AwsLinkedConfigInput>;
  awsRootConfig?: InputMaybe<AwsRootConfigInput>;
  azureSubscriptionConfig?: InputMaybe<AzureSubscriptionConfigInput>;
  azureTenantConfig?: InputMaybe<AzureTenantConfigInput>;
  databricksConfig?: InputMaybe<DatabricksConfigInput>;
  gcpConfig?: InputMaybe<GcpConfigInput>;
  gcpTenantConfig?: InputMaybe<GcpTenantConfigInput>;
  k8sConfig?: InputMaybe<K8sConfigInput>;
  name?: InputMaybe<Scalars["String"]["input"]>;
  nebiusConfig?: InputMaybe<NebiusConfigInput>;
  type?: InputMaybe<Scalars["String"]["input"]>;
};

export type DataSourceDetails = {
  __typename?: "DataSourceDetails";
  cost: Scalars["Float"]["output"];
  discovery_infos?: Maybe<Array<Maybe<DataSourceDiscoveryInfos>>>;
  forecast: Scalars["Float"]["output"];
  last_month_cost?: Maybe<Scalars["Float"]["output"]>;
  resources: Scalars["Int"]["output"];
};

export type DataSourceDiscoveryInfos = {
  __typename?: "DataSourceDiscoveryInfos";
  cloud_account_id: Scalars["String"]["output"];
  created_at: Scalars["Int"]["output"];
  deleted_at: Scalars["Int"]["output"];
  enabled?: Maybe<Scalars["Boolean"]["output"]>;
  id: Scalars["String"]["output"];
  last_discovery_at: Scalars["Int"]["output"];
  last_error?: Maybe<Scalars["String"]["output"]>;
  last_error_at: Scalars["Int"]["output"];
  observe_time: Scalars["Int"]["output"];
  resource_type?: Maybe<Scalars["String"]["output"]>;
};

export type DataSourceInterface = {
  account_id?: Maybe<Scalars["String"]["output"]>;
  created_at?: Maybe<Scalars["Int"]["output"]>;
  details?: Maybe<DataSourceDetails>;
  id?: Maybe<Scalars["String"]["output"]>;
  last_getting_metric_attempt_at?: Maybe<Scalars["Int"]["output"]>;
  last_getting_metric_attempt_error?: Maybe<Scalars["String"]["output"]>;
  last_getting_metrics_at?: Maybe<Scalars["Int"]["output"]>;
  last_import_at?: Maybe<Scalars["Int"]["output"]>;
  last_import_attempt_at?: Maybe<Scalars["Int"]["output"]>;
  last_import_attempt_error?: Maybe<Scalars["String"]["output"]>;
  name?: Maybe<Scalars["String"]["output"]>;
  parent_id?: Maybe<Scalars["String"]["output"]>;
  type?: Maybe<DataSourceType>;
};

export type DataSourceRequestParams = {
  details?: InputMaybe<Scalars["Boolean"]["input"]>;
};

export type DataSourceType =
  | "alibaba_cnr"
  | "aws_cnr"
  | "azure_cnr"
  | "azure_tenant"
  | "databricks"
  | "environment"
  | "gcp_cnr"
  | "gcp_tenant"
  | "kubernetes_cnr"
  | "nebius";

export type DatabricksConfig = {
  __typename?: "DatabricksConfig";
  account_id?: Maybe<Scalars["String"]["output"]>;
  client_id?: Maybe<Scalars["String"]["output"]>;
};

export type DatabricksConfigInput = {
  account_id: Scalars["String"]["input"];
  client_id: Scalars["String"]["input"];
  client_secret: Scalars["String"]["input"];
};

export type DatabricksDataSource = DataSourceInterface & {
  __typename?: "DatabricksDataSource";
  account_id: Scalars["String"]["output"];
  config?: Maybe<DatabricksConfig>;
  created_at?: Maybe<Scalars["Int"]["output"]>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars["String"]["output"];
  last_getting_metric_attempt_at: Scalars["Int"]["output"];
  last_getting_metric_attempt_error?: Maybe<Scalars["String"]["output"]>;
  last_getting_metrics_at: Scalars["Int"]["output"];
  last_import_at: Scalars["Int"]["output"];
  last_import_attempt_at: Scalars["Int"]["output"];
  last_import_attempt_error?: Maybe<Scalars["String"]["output"]>;
  name: Scalars["String"]["output"];
  parent_id?: Maybe<Scalars["String"]["output"]>;
  type: DataSourceType;
};

export type Employee = {
  __typename?: "Employee";
  id: Scalars["String"]["output"];
  jira_connected: Scalars["Boolean"]["output"];
  slack_connected: Scalars["Boolean"]["output"];
};

export type EmployeeEmail = {
  __typename?: "EmployeeEmail";
  available_by_role: Scalars["Boolean"]["output"];
  email_template: Scalars["String"]["output"];
  employee_id: Scalars["ID"]["output"];
  enabled: Scalars["Boolean"]["output"];
  id: Scalars["ID"]["output"];
};

export type EnvironmentDataSource = DataSourceInterface & {
  __typename?: "EnvironmentDataSource";
  account_id: Scalars["String"]["output"];
  created_at?: Maybe<Scalars["Int"]["output"]>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars["String"]["output"];
  last_getting_metric_attempt_at: Scalars["Int"]["output"];
  last_getting_metric_attempt_error?: Maybe<Scalars["String"]["output"]>;
  last_getting_metrics_at: Scalars["Int"]["output"];
  last_import_at: Scalars["Int"]["output"];
  last_import_attempt_at: Scalars["Int"]["output"];
  last_import_attempt_error?: Maybe<Scalars["String"]["output"]>;
  name: Scalars["String"]["output"];
  parent_id?: Maybe<Scalars["String"]["output"]>;
  type: DataSourceType;
};

export type ExpensesDailyBreakdown = {
  __typename?: "ExpensesDailyBreakdown";
  breakdown: Scalars["JSONObject"]["output"];
  breakdown_by: BreakdownBy;
  counts: Scalars["JSONObject"]["output"];
  previous_range_start: Scalars["Int"]["output"];
  previous_total: Scalars["Int"]["output"];
  start_date: Scalars["Int"]["output"];
  total: Scalars["Int"]["output"];
};

export type GcpBillingDataConfig = {
  __typename?: "GcpBillingDataConfig";
  dataset_name: Scalars["String"]["output"];
  project_id?: Maybe<Scalars["String"]["output"]>;
  table_name: Scalars["String"]["output"];
};

export type GcpBillingDataConfigInput = {
  dataset_name: Scalars["String"]["input"];
  project_id?: InputMaybe<Scalars["String"]["input"]>;
  table_name: Scalars["String"]["input"];
};

export type GcpConfig = {
  __typename?: "GcpConfig";
  billing_data?: Maybe<GcpBillingDataConfig>;
  pricing_data?: Maybe<GcpPricingDataConfig>;
};

export type GcpConfigInput = {
  billing_data: GcpBillingDataConfigInput;
  credentials: Scalars["JSONObject"]["input"];
  pricing_data?: InputMaybe<GcpPricingDataConfigInput>;
};

export type GcpDataSource = DataSourceInterface & {
  __typename?: "GcpDataSource";
  account_id: Scalars["String"]["output"];
  config?: Maybe<GcpConfig>;
  created_at?: Maybe<Scalars["Int"]["output"]>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars["String"]["output"];
  last_getting_metric_attempt_at: Scalars["Int"]["output"];
  last_getting_metric_attempt_error?: Maybe<Scalars["String"]["output"]>;
  last_getting_metrics_at: Scalars["Int"]["output"];
  last_import_at: Scalars["Int"]["output"];
  last_import_attempt_at: Scalars["Int"]["output"];
  last_import_attempt_error?: Maybe<Scalars["String"]["output"]>;
  name: Scalars["String"]["output"];
  parent_id?: Maybe<Scalars["String"]["output"]>;
  type: DataSourceType;
};

export type GcpPricingDataConfig = {
  __typename?: "GcpPricingDataConfig";
  dataset_name: Scalars["String"]["output"];
  project_id?: Maybe<Scalars["String"]["output"]>;
  table_name: Scalars["String"]["output"];
};

export type GcpPricingDataConfigInput = {
  dataset_name: Scalars["String"]["input"];
  project_id?: InputMaybe<Scalars["String"]["input"]>;
  table_name: Scalars["String"]["input"];
};

export type GcpTenantBillingDataConfig = {
  __typename?: "GcpTenantBillingDataConfig";
  dataset_name: Scalars["String"]["output"];
  project_id?: Maybe<Scalars["String"]["output"]>;
  table_name: Scalars["String"]["output"];
};

export type GcpTenantConfig = {
  __typename?: "GcpTenantConfig";
  billing_data?: Maybe<GcpTenantBillingDataConfig>;
  pricing_data?: Maybe<GcpTenantPricingDataConfig>;
};

export type GcpTenantConfigInput = {
  billing_data: GcpBillingDataConfigInput;
  credentials: Scalars["JSONObject"]["input"];
  pricing_data?: InputMaybe<GcpPricingDataConfigInput>;
};

export type GcpTenantDataSource = DataSourceInterface & {
  __typename?: "GcpTenantDataSource";
  account_id?: Maybe<Scalars["String"]["output"]>;
  config?: Maybe<GcpTenantConfig>;
  created_at?: Maybe<Scalars["Int"]["output"]>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars["String"]["output"];
  last_getting_metric_attempt_at: Scalars["Int"]["output"];
  last_getting_metric_attempt_error?: Maybe<Scalars["String"]["output"]>;
  last_getting_metrics_at: Scalars["Int"]["output"];
  last_import_at: Scalars["Int"]["output"];
  last_import_attempt_at: Scalars["Int"]["output"];
  last_import_attempt_error?: Maybe<Scalars["String"]["output"]>;
  name: Scalars["String"]["output"];
  parent_id?: Maybe<Scalars["String"]["output"]>;
  type: DataSourceType;
};

export type GcpTenantPricingDataConfig = {
  __typename?: "GcpTenantPricingDataConfig";
  dataset_name: Scalars["String"]["output"];
  project_id?: Maybe<Scalars["String"]["output"]>;
  table_name: Scalars["String"]["output"];
};

export type Invitation = {
  __typename?: "Invitation";
  id: Scalars["String"]["output"];
  invite_assignments?: Maybe<Array<InvitationAssignment>>;
  organization: Scalars["String"]["output"];
  owner_email: Scalars["String"]["output"];
  owner_name: Scalars["String"]["output"];
};

export type InvitationAssignment = {
  __typename?: "InvitationAssignment";
  id: Scalars["String"]["output"];
  purpose: Scalars["String"]["output"];
  scope_id: Scalars["String"]["output"];
  scope_name: Scalars["String"]["output"];
  scope_type: Scalars["String"]["output"];
};

export type K8CostModelConfig = {
  __typename?: "K8CostModelConfig";
  cpu_hourly_cost: Scalars["Float"]["output"];
  memory_hourly_cost: Scalars["Float"]["output"];
};

export type K8sConfig = {
  __typename?: "K8sConfig";
  cost_model?: Maybe<K8CostModelConfig>;
  custom_price?: Maybe<Scalars["Boolean"]["output"]>;
  user?: Maybe<Scalars["String"]["output"]>;
};

export type K8sConfigInput = {
  cost_model?: InputMaybe<Scalars["JSONObject"]["input"]>;
  custom_price?: InputMaybe<Scalars["Boolean"]["input"]>;
  password: Scalars["String"]["input"];
  user: Scalars["String"]["input"];
};

export type K8sDataSource = DataSourceInterface & {
  __typename?: "K8sDataSource";
  account_id: Scalars["String"]["output"];
  config?: Maybe<K8sConfig>;
  created_at?: Maybe<Scalars["Int"]["output"]>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars["String"]["output"];
  last_getting_metric_attempt_at: Scalars["Int"]["output"];
  last_getting_metric_attempt_error?: Maybe<Scalars["String"]["output"]>;
  last_getting_metrics_at: Scalars["Int"]["output"];
  last_import_at: Scalars["Int"]["output"];
  last_import_attempt_at: Scalars["Int"]["output"];
  last_import_attempt_error?: Maybe<Scalars["String"]["output"]>;
  name: Scalars["String"]["output"];
  parent_id?: Maybe<Scalars["String"]["output"]>;
  type: DataSourceType;
};

export type MetaBreakdown = {
  __typename?: "MetaBreakdown";
  breakdown: Scalars["JSONObject"]["output"];
  end_date: Scalars["Int"]["output"];
  start_date: Scalars["Int"]["output"];
  totals: Scalars["JSONObject"]["output"];
};

export type Mutation = {
  __typename?: "Mutation";
  _empty?: Maybe<Scalars["String"]["output"]>;
  createDataSource?: Maybe<DataSourceInterface>;
  createOrganization?: Maybe<Organization>;
  deleteDataSource?: Maybe<Scalars["String"]["output"]>;
  deleteOrganization?: Maybe<Scalars["String"]["output"]>;
  updateDataSource?: Maybe<DataSourceInterface>;
  updateEmployeeEmail?: Maybe<EmployeeEmail>;
  updateEmployeeEmails?: Maybe<Array<Maybe<EmployeeEmail>>>;
  updateInvitation?: Maybe<Scalars["String"]["output"]>;
  updateOrganization?: Maybe<Organization>;
  updateOrganizationPerspectives?: Maybe<Scalars["JSONObject"]["output"]>;
  updateOrganizationThemeSettings?: Maybe<Scalars["JSONObject"]["output"]>;
};

export type MutationCreateDataSourceArgs = {
  organizationId: Scalars["ID"]["input"];
  params: CreateDataSourceInput;
};

export type MutationCreateOrganizationArgs = {
  organizationName: Scalars["String"]["input"];
};

export type MutationDeleteDataSourceArgs = {
  dataSourceId: Scalars["ID"]["input"];
};

export type MutationDeleteOrganizationArgs = {
  organizationId: Scalars["ID"]["input"];
};

export type MutationUpdateDataSourceArgs = {
  dataSourceId: Scalars["ID"]["input"];
  params: UpdateDataSourceInput;
};

export type MutationUpdateEmployeeEmailArgs = {
  employeeId: Scalars["ID"]["input"];
  params: UpdateEmployeeEmailInput;
};

export type MutationUpdateEmployeeEmailsArgs = {
  employeeId: Scalars["ID"]["input"];
  params: UpdateEmployeeEmailsInput;
};

export type MutationUpdateInvitationArgs = {
  action: Scalars["String"]["input"];
  invitationId: Scalars["String"]["input"];
};

export type MutationUpdateOrganizationArgs = {
  organizationId: Scalars["ID"]["input"];
  params: UpdateOrganizationInput;
};

export type MutationUpdateOrganizationPerspectivesArgs = {
  organizationId: Scalars["ID"]["input"];
  value: Scalars["JSONObject"]["input"];
};

export type MutationUpdateOrganizationThemeSettingsArgs = {
  organizationId: Scalars["ID"]["input"];
  value: Scalars["JSONObject"]["input"];
};

export type NebiusConfig = {
  __typename?: "NebiusConfig";
  access_key_id?: Maybe<Scalars["String"]["output"]>;
  bucket_name?: Maybe<Scalars["String"]["output"]>;
  bucket_prefix?: Maybe<Scalars["String"]["output"]>;
  cloud_name?: Maybe<Scalars["String"]["output"]>;
  key_id?: Maybe<Scalars["String"]["output"]>;
  service_account_id?: Maybe<Scalars["String"]["output"]>;
};

export type NebiusConfigInput = {
  access_key_id: Scalars["String"]["input"];
  bucket_name: Scalars["String"]["input"];
  bucket_prefix?: InputMaybe<Scalars["String"]["input"]>;
  cloud_name: Scalars["String"]["input"];
  key_id: Scalars["String"]["input"];
  private_key: Scalars["String"]["input"];
  secret_access_key: Scalars["String"]["input"];
  service_account_id: Scalars["String"]["input"];
};

export type NebiusDataSource = DataSourceInterface & {
  __typename?: "NebiusDataSource";
  account_id: Scalars["String"]["output"];
  config?: Maybe<NebiusConfig>;
  created_at?: Maybe<Scalars["Int"]["output"]>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars["String"]["output"];
  last_getting_metric_attempt_at: Scalars["Int"]["output"];
  last_getting_metric_attempt_error?: Maybe<Scalars["String"]["output"]>;
  last_getting_metrics_at: Scalars["Int"]["output"];
  last_import_at: Scalars["Int"]["output"];
  last_import_attempt_at: Scalars["Int"]["output"];
  last_import_attempt_error?: Maybe<Scalars["String"]["output"]>;
  name: Scalars["String"]["output"];
  parent_id?: Maybe<Scalars["String"]["output"]>;
  type: DataSourceType;
};

export type Organization = {
  __typename?: "Organization";
  currency: Scalars["String"]["output"];
  disabled: Scalars["Boolean"]["output"];
  id: Scalars["String"]["output"];
  is_demo: Scalars["Boolean"]["output"];
  name: Scalars["String"]["output"];
  pool_id: Scalars["String"]["output"];
};

export type OrganizationConstraint = {
  __typename?: "OrganizationConstraint";
  created_at: Scalars["Int"]["output"];
  definition: Scalars["JSONObject"]["output"];
  deleted_at: Scalars["Int"]["output"];
  filters: Scalars["JSONObject"]["output"];
  id: Scalars["ID"]["output"];
  last_run: Scalars["Int"]["output"];
  last_run_result: Scalars["JSONObject"]["output"];
  name: Scalars["String"]["output"];
  organization_id: Scalars["String"]["output"];
  type: OrganizationConstraintType;
};

export type OrganizationConstraintType =
  | "expense_anomaly"
  | "expiring_budget"
  | "recurring_budget"
  | "resource_count_anomaly"
  | "resource_quota"
  | "tagging_policy";

export type OrganizationLimitHit = {
  __typename?: "OrganizationLimitHit";
  constraint_id: Scalars["String"]["output"];
  constraint_limit: Scalars["Float"]["output"];
  created_at: Scalars["Int"]["output"];
  deleted_at: Scalars["Int"]["output"];
  id: Scalars["ID"]["output"];
  organization_id: Scalars["String"]["output"];
  run_result: Scalars["JSONObject"]["output"];
  value: Scalars["Float"]["output"];
};

export type Query = {
  __typename?: "Query";
  _empty?: Maybe<Scalars["String"]["output"]>;
  availableFilters?: Maybe<Scalars["JSONObject"]["output"]>;
  cleanExpenses?: Maybe<Scalars["JSONObject"]["output"]>;
  cloudPolicies?: Maybe<Scalars["JSONObject"]["output"]>;
  currentEmployee?: Maybe<Employee>;
  dataSource?: Maybe<DataSourceInterface>;
  dataSources?: Maybe<Array<Maybe<DataSourceInterface>>>;
  employeeEmails?: Maybe<Array<Maybe<EmployeeEmail>>>;
  expensesDailyBreakdown?: Maybe<ExpensesDailyBreakdown>;
  invitations?: Maybe<Array<Maybe<Invitation>>>;
  metaBreakdown?: Maybe<MetaBreakdown>;
  organizationConstraint?: Maybe<OrganizationConstraint>;
  organizationFeatures?: Maybe<Scalars["JSONObject"]["output"]>;
  organizationLimitHits?: Maybe<Array<OrganizationLimitHit>>;
  organizationPerspectives?: Maybe<Scalars["JSONObject"]["output"]>;
  organizationThemeSettings?: Maybe<Scalars["JSONObject"]["output"]>;
  organizations: Array<Organization>;
  relevantFlavors?: Maybe<Scalars["JSONObject"]["output"]>;
  resourceCountBreakdown?: Maybe<ResourceCountBreakdown>;
};

export type QueryAvailableFiltersArgs = {
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<AvailableFiltersParams>;
};

export type QueryCleanExpensesArgs = {
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<CleanExpensesParams>;
};

export type QueryCloudPoliciesArgs = {
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<CloudPoliciesParams>;
};

export type QueryCurrentEmployeeArgs = {
  organizationId: Scalars["ID"]["input"];
};

export type QueryDataSourceArgs = {
  dataSourceId: Scalars["ID"]["input"];
  requestParams?: InputMaybe<DataSourceRequestParams>;
};

export type QueryDataSourcesArgs = {
  organizationId: Scalars["ID"]["input"];
};

export type QueryEmployeeEmailsArgs = {
  employeeId: Scalars["ID"]["input"];
};

export type QueryExpensesDailyBreakdownArgs = {
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<BreakdownParams>;
};

export type QueryMetaBreakdownArgs = {
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<BreakdownParams>;
};

export type QueryOrganizationConstraintArgs = {
  constraintId: Scalars["ID"]["input"];
};

export type QueryOrganizationFeaturesArgs = {
  organizationId: Scalars["ID"]["input"];
};

export type QueryOrganizationLimitHitsArgs = {
  constraintId: Scalars["ID"]["input"];
  organizationId: Scalars["ID"]["input"];
};

export type QueryOrganizationPerspectivesArgs = {
  organizationId: Scalars["ID"]["input"];
};

export type QueryOrganizationThemeSettingsArgs = {
  organizationId: Scalars["ID"]["input"];
};

export type QueryRelevantFlavorsArgs = {
  organizationId: Scalars["ID"]["input"];
  requestParams?: InputMaybe<Scalars["JSONObject"]["input"]>;
};

export type QueryResourceCountBreakdownArgs = {
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<BreakdownParams>;
};

export type ResourceCountBreakdown = {
  __typename?: "ResourceCountBreakdown";
  breakdown: Scalars["JSONObject"]["output"];
  breakdown_by: BreakdownBy;
  count: Scalars["Int"]["output"];
  counts: Scalars["JSONObject"]["output"];
  end_date: Scalars["Int"]["output"];
  first_breakdown: Scalars["Int"]["output"];
  last_breakdown: Scalars["Int"]["output"];
  start_date: Scalars["Int"]["output"];
};

export type UpdateDataSourceInput = {
  alibabaConfig?: InputMaybe<AlibabaConfigInput>;
  awsAssumedRoleConfig?: InputMaybe<AwsAssumedRoleConfigInput>;
  awsLinkedConfig?: InputMaybe<AwsLinkedConfigInput>;
  awsRootConfig?: InputMaybe<AwsRootConfigInput>;
  azureSubscriptionConfig?: InputMaybe<AzureSubscriptionConfigInput>;
  azureTenantConfig?: InputMaybe<AzureTenantConfigInput>;
  databricksConfig?: InputMaybe<DatabricksConfigInput>;
  gcpConfig?: InputMaybe<GcpConfigInput>;
  gcpTenantConfig?: InputMaybe<GcpTenantConfigInput>;
  k8sConfig?: InputMaybe<K8sConfigInput>;
  lastImportAt?: InputMaybe<Scalars["Int"]["input"]>;
  lastImportModifiedAt?: InputMaybe<Scalars["Int"]["input"]>;
  name?: InputMaybe<Scalars["String"]["input"]>;
  nebiusConfig?: InputMaybe<NebiusConfigInput>;
};

export type UpdateEmployeeEmailInput = {
  action: UpdateEmployeeEmailsAction;
  emailId: Scalars["ID"]["input"];
};

export type UpdateEmployeeEmailsAction = "disable" | "enable";

export type UpdateEmployeeEmailsInput = {
  disable?: InputMaybe<Array<Scalars["ID"]["input"]>>;
  enable?: InputMaybe<Array<Scalars["ID"]["input"]>>;
};

export type UpdateOrganizationInput = {
  currency?: InputMaybe<Scalars["String"]["input"]>;
  name?: InputMaybe<Scalars["String"]["input"]>;
};

export type AwsDataSourceConfigFragmentFragment = {
  __typename?: "AwsDataSource";
  config?: {
    __typename?: "AwsConfig";
    assume_role_account_id?: string | null;
    assume_role_name?: string | null;
    access_key_id?: string | null;
    linked?: boolean | null;
    use_edp_discount?: boolean | null;
    cur_version?: number | null;
    bucket_name?: string | null;
    bucket_prefix?: string | null;
    config_scheme?: string | null;
    region_name?: string | null;
    report_name?: string | null;
  } | null;
};

export type AzureTenantDataSourceConfigFragmentFragment = {
  __typename?: "AzureTenantDataSource";
  config?: { __typename?: "AzureTenantConfig"; client_id?: string | null; tenant?: string | null } | null;
};

export type AzureSubscriptionDataSourceConfigFragmentFragment = {
  __typename?: "AzureSubscriptionDataSource";
  config?: {
    __typename?: "AzureSubscriptionConfig";
    client_id?: string | null;
    expense_import_scheme?: string | null;
    subscription_id?: string | null;
    tenant?: string | null;
    export_name?: string | null;
    container?: string | null;
    directory?: string | null;
  } | null;
};

export type GcpDataSourceConfigFragmentFragment = {
  __typename?: "GcpDataSource";
  config?: {
    __typename?: "GcpConfig";
    billing_data?: {
      __typename?: "GcpBillingDataConfig";
      dataset_name: string;
      table_name: string;
      project_id?: string | null;
    } | null;
    pricing_data?: {
      __typename?: "GcpPricingDataConfig";
      dataset_name: string;
      table_name: string;
      project_id?: string | null;
    } | null;
  } | null;
};

export type GcpTenantDataSourceConfigFragmentFragment = {
  __typename?: "GcpTenantDataSource";
  config?: {
    __typename?: "GcpTenantConfig";
    billing_data?: {
      __typename?: "GcpTenantBillingDataConfig";
      dataset_name: string;
      table_name: string;
      project_id?: string | null;
    } | null;
    pricing_data?: {
      __typename?: "GcpTenantPricingDataConfig";
      dataset_name: string;
      table_name: string;
      project_id?: string | null;
    } | null;
  } | null;
};

export type AlibabaDataSourceConfigFragmentFragment = {
  __typename?: "AlibabaDataSource";
  config?: { __typename?: "AlibabaConfig"; access_key_id?: string | null } | null;
};

export type NebiusDataSourceConfigFragmentFragment = {
  __typename?: "NebiusDataSource";
  config?: {
    __typename?: "NebiusConfig";
    cloud_name?: string | null;
    service_account_id?: string | null;
    key_id?: string | null;
    access_key_id?: string | null;
    bucket_name?: string | null;
    bucket_prefix?: string | null;
  } | null;
};

export type DatabricksDataSourceConfigFragmentFragment = {
  __typename?: "DatabricksDataSource";
  config?: { __typename?: "DatabricksConfig"; account_id?: string | null; client_id?: string | null } | null;
};

export type K8sDataSourceConfigFragmentFragment = {
  __typename?: "K8sDataSource";
  config?: {
    __typename?: "K8sConfig";
    custom_price?: boolean | null;
    user?: string | null;
    cost_model?: { __typename?: "K8CostModelConfig"; cpu_hourly_cost: number; memory_hourly_cost: number } | null;
  } | null;
};

export type OrganizationsQueryVariables = Exact<{ [key: string]: never }>;

export type OrganizationsQuery = {
  __typename?: "Query";
  organizations: Array<{
    __typename?: "Organization";
    id: string;
    name: string;
    pool_id: string;
    currency: string;
    is_demo: boolean;
    disabled: boolean;
  }>;
};

export type CreateOrganizationMutationVariables = Exact<{
  organizationName: Scalars["String"]["input"];
}>;

export type CreateOrganizationMutation = {
  __typename?: "Mutation";
  createOrganization?: { __typename?: "Organization"; id: string; name: string } | null;
};

export type UpdateOrganizationMutationVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  params: UpdateOrganizationInput;
}>;

export type UpdateOrganizationMutation = {
  __typename?: "Mutation";
  updateOrganization?: { __typename?: "Organization"; id: string; name: string; currency: string } | null;
};

export type DeleteOrganizationMutationVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
}>;

export type DeleteOrganizationMutation = { __typename?: "Mutation"; deleteOrganization?: string | null };

export type CurrentEmployeeQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
}>;

export type CurrentEmployeeQuery = {
  __typename?: "Query";
  currentEmployee?: { __typename?: "Employee"; id: string; jira_connected: boolean; slack_connected: boolean } | null;
};

export type DataSourcesQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
}>;

export type DataSourcesQuery = {
  __typename?: "Query";
  dataSources?: Array<
    | {
        __typename?: "AlibabaDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          resources: number;
          forecast: number;
          last_month_cost?: number | null;
        } | null;
        config?: { __typename?: "AlibabaConfig"; access_key_id?: string | null } | null;
      }
    | {
        __typename?: "AwsDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          resources: number;
          forecast: number;
          last_month_cost?: number | null;
        } | null;
        config?: {
          __typename?: "AwsConfig";
          assume_role_account_id?: string | null;
          assume_role_name?: string | null;
          access_key_id?: string | null;
          linked?: boolean | null;
          use_edp_discount?: boolean | null;
          cur_version?: number | null;
          bucket_name?: string | null;
          bucket_prefix?: string | null;
          config_scheme?: string | null;
          region_name?: string | null;
          report_name?: string | null;
        } | null;
      }
    | {
        __typename?: "AzureSubscriptionDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          resources: number;
          forecast: number;
          last_month_cost?: number | null;
        } | null;
        config?: {
          __typename?: "AzureSubscriptionConfig";
          client_id?: string | null;
          expense_import_scheme?: string | null;
          subscription_id?: string | null;
          tenant?: string | null;
          export_name?: string | null;
          container?: string | null;
          directory?: string | null;
        } | null;
      }
    | {
        __typename?: "AzureTenantDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          resources: number;
          forecast: number;
          last_month_cost?: number | null;
        } | null;
        config?: { __typename?: "AzureTenantConfig"; client_id?: string | null; tenant?: string | null } | null;
      }
    | {
        __typename?: "DatabricksDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          resources: number;
          forecast: number;
          last_month_cost?: number | null;
        } | null;
        config?: { __typename?: "DatabricksConfig"; account_id?: string | null; client_id?: string | null } | null;
      }
    | {
        __typename?: "EnvironmentDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          resources: number;
          forecast: number;
          last_month_cost?: number | null;
        } | null;
      }
    | {
        __typename?: "GcpDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          resources: number;
          forecast: number;
          last_month_cost?: number | null;
        } | null;
        config?: {
          __typename?: "GcpConfig";
          billing_data?: {
            __typename?: "GcpBillingDataConfig";
            dataset_name: string;
            table_name: string;
            project_id?: string | null;
          } | null;
          pricing_data?: {
            __typename?: "GcpPricingDataConfig";
            dataset_name: string;
            table_name: string;
            project_id?: string | null;
          } | null;
        } | null;
      }
    | {
        __typename?: "GcpTenantDataSource";
        account_id?: string | null;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          resources: number;
          forecast: number;
          last_month_cost?: number | null;
        } | null;
        config?: {
          __typename?: "GcpTenantConfig";
          billing_data?: {
            __typename?: "GcpTenantBillingDataConfig";
            dataset_name: string;
            table_name: string;
            project_id?: string | null;
          } | null;
          pricing_data?: {
            __typename?: "GcpTenantPricingDataConfig";
            dataset_name: string;
            table_name: string;
            project_id?: string | null;
          } | null;
        } | null;
      }
    | {
        __typename?: "K8sDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          resources: number;
          forecast: number;
          last_month_cost?: number | null;
        } | null;
        config?: {
          __typename?: "K8sConfig";
          custom_price?: boolean | null;
          user?: string | null;
          cost_model?: { __typename?: "K8CostModelConfig"; cpu_hourly_cost: number; memory_hourly_cost: number } | null;
        } | null;
      }
    | {
        __typename?: "NebiusDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          resources: number;
          forecast: number;
          last_month_cost?: number | null;
        } | null;
        config?: {
          __typename?: "NebiusConfig";
          cloud_name?: string | null;
          service_account_id?: string | null;
          key_id?: string | null;
          access_key_id?: string | null;
          bucket_name?: string | null;
          bucket_prefix?: string | null;
        } | null;
      }
    | null
  > | null;
};

export type DataSourceQueryVariables = Exact<{
  dataSourceId: Scalars["ID"]["input"];
  requestParams?: InputMaybe<DataSourceRequestParams>;
}>;

export type DataSourceQuery = {
  __typename?: "Query";
  dataSource?:
    | {
        __typename?: "AlibabaDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          forecast: number;
          last_month_cost?: number | null;
          resources: number;
          discovery_infos?: Array<{
            __typename?: "DataSourceDiscoveryInfos";
            cloud_account_id: string;
            created_at: number;
            deleted_at: number;
            enabled?: boolean | null;
            id: string;
            last_discovery_at: number;
            last_error?: string | null;
            last_error_at: number;
            observe_time: number;
            resource_type?: string | null;
          } | null> | null;
        } | null;
        config?: { __typename?: "AlibabaConfig"; access_key_id?: string | null } | null;
      }
    | {
        __typename?: "AwsDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          forecast: number;
          last_month_cost?: number | null;
          resources: number;
          discovery_infos?: Array<{
            __typename?: "DataSourceDiscoveryInfos";
            cloud_account_id: string;
            created_at: number;
            deleted_at: number;
            enabled?: boolean | null;
            id: string;
            last_discovery_at: number;
            last_error?: string | null;
            last_error_at: number;
            observe_time: number;
            resource_type?: string | null;
          } | null> | null;
        } | null;
        config?: {
          __typename?: "AwsConfig";
          assume_role_account_id?: string | null;
          assume_role_name?: string | null;
          access_key_id?: string | null;
          linked?: boolean | null;
          use_edp_discount?: boolean | null;
          cur_version?: number | null;
          bucket_name?: string | null;
          bucket_prefix?: string | null;
          config_scheme?: string | null;
          region_name?: string | null;
          report_name?: string | null;
        } | null;
      }
    | {
        __typename?: "AzureSubscriptionDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          forecast: number;
          last_month_cost?: number | null;
          resources: number;
          discovery_infos?: Array<{
            __typename?: "DataSourceDiscoveryInfos";
            cloud_account_id: string;
            created_at: number;
            deleted_at: number;
            enabled?: boolean | null;
            id: string;
            last_discovery_at: number;
            last_error?: string | null;
            last_error_at: number;
            observe_time: number;
            resource_type?: string | null;
          } | null> | null;
        } | null;
        config?: {
          __typename?: "AzureSubscriptionConfig";
          client_id?: string | null;
          expense_import_scheme?: string | null;
          subscription_id?: string | null;
          tenant?: string | null;
          export_name?: string | null;
          container?: string | null;
          directory?: string | null;
        } | null;
      }
    | {
        __typename?: "AzureTenantDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          forecast: number;
          last_month_cost?: number | null;
          resources: number;
          discovery_infos?: Array<{
            __typename?: "DataSourceDiscoveryInfos";
            cloud_account_id: string;
            created_at: number;
            deleted_at: number;
            enabled?: boolean | null;
            id: string;
            last_discovery_at: number;
            last_error?: string | null;
            last_error_at: number;
            observe_time: number;
            resource_type?: string | null;
          } | null> | null;
        } | null;
        config?: { __typename?: "AzureTenantConfig"; client_id?: string | null; tenant?: string | null } | null;
      }
    | {
        __typename?: "DatabricksDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          forecast: number;
          last_month_cost?: number | null;
          resources: number;
          discovery_infos?: Array<{
            __typename?: "DataSourceDiscoveryInfos";
            cloud_account_id: string;
            created_at: number;
            deleted_at: number;
            enabled?: boolean | null;
            id: string;
            last_discovery_at: number;
            last_error?: string | null;
            last_error_at: number;
            observe_time: number;
            resource_type?: string | null;
          } | null> | null;
        } | null;
        config?: { __typename?: "DatabricksConfig"; account_id?: string | null; client_id?: string | null } | null;
      }
    | {
        __typename?: "EnvironmentDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          forecast: number;
          last_month_cost?: number | null;
          resources: number;
          discovery_infos?: Array<{
            __typename?: "DataSourceDiscoveryInfos";
            cloud_account_id: string;
            created_at: number;
            deleted_at: number;
            enabled?: boolean | null;
            id: string;
            last_discovery_at: number;
            last_error?: string | null;
            last_error_at: number;
            observe_time: number;
            resource_type?: string | null;
          } | null> | null;
        } | null;
      }
    | {
        __typename?: "GcpDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          forecast: number;
          last_month_cost?: number | null;
          resources: number;
          discovery_infos?: Array<{
            __typename?: "DataSourceDiscoveryInfos";
            cloud_account_id: string;
            created_at: number;
            deleted_at: number;
            enabled?: boolean | null;
            id: string;
            last_discovery_at: number;
            last_error?: string | null;
            last_error_at: number;
            observe_time: number;
            resource_type?: string | null;
          } | null> | null;
        } | null;
        config?: {
          __typename?: "GcpConfig";
          billing_data?: {
            __typename?: "GcpBillingDataConfig";
            dataset_name: string;
            table_name: string;
            project_id?: string | null;
          } | null;
          pricing_data?: {
            __typename?: "GcpPricingDataConfig";
            dataset_name: string;
            table_name: string;
            project_id?: string | null;
          } | null;
        } | null;
      }
    | {
        __typename?: "GcpTenantDataSource";
        account_id?: string | null;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          forecast: number;
          last_month_cost?: number | null;
          resources: number;
          discovery_infos?: Array<{
            __typename?: "DataSourceDiscoveryInfos";
            cloud_account_id: string;
            created_at: number;
            deleted_at: number;
            enabled?: boolean | null;
            id: string;
            last_discovery_at: number;
            last_error?: string | null;
            last_error_at: number;
            observe_time: number;
            resource_type?: string | null;
          } | null> | null;
        } | null;
        config?: {
          __typename?: "GcpTenantConfig";
          billing_data?: {
            __typename?: "GcpTenantBillingDataConfig";
            dataset_name: string;
            table_name: string;
            project_id?: string | null;
          } | null;
          pricing_data?: {
            __typename?: "GcpTenantPricingDataConfig";
            dataset_name: string;
            table_name: string;
            project_id?: string | null;
          } | null;
        } | null;
      }
    | {
        __typename?: "K8sDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          forecast: number;
          last_month_cost?: number | null;
          resources: number;
          discovery_infos?: Array<{
            __typename?: "DataSourceDiscoveryInfos";
            cloud_account_id: string;
            created_at: number;
            deleted_at: number;
            enabled?: boolean | null;
            id: string;
            last_discovery_at: number;
            last_error?: string | null;
            last_error_at: number;
            observe_time: number;
            resource_type?: string | null;
          } | null> | null;
        } | null;
        config?: {
          __typename?: "K8sConfig";
          custom_price?: boolean | null;
          user?: string | null;
          cost_model?: { __typename?: "K8CostModelConfig"; cpu_hourly_cost: number; memory_hourly_cost: number } | null;
        } | null;
      }
    | {
        __typename?: "NebiusDataSource";
        account_id: string;
        created_at?: number | null;
        id: string;
        last_getting_metric_attempt_at: number;
        last_getting_metric_attempt_error?: string | null;
        last_getting_metrics_at: number;
        last_import_at: number;
        last_import_attempt_at: number;
        last_import_attempt_error?: string | null;
        name: string;
        parent_id?: string | null;
        type: DataSourceType;
        details?: {
          __typename?: "DataSourceDetails";
          cost: number;
          forecast: number;
          last_month_cost?: number | null;
          resources: number;
          discovery_infos?: Array<{
            __typename?: "DataSourceDiscoveryInfos";
            cloud_account_id: string;
            created_at: number;
            deleted_at: number;
            enabled?: boolean | null;
            id: string;
            last_discovery_at: number;
            last_error?: string | null;
            last_error_at: number;
            observe_time: number;
            resource_type?: string | null;
          } | null> | null;
        } | null;
        config?: {
          __typename?: "NebiusConfig";
          cloud_name?: string | null;
          service_account_id?: string | null;
          key_id?: string | null;
          access_key_id?: string | null;
          bucket_name?: string | null;
          bucket_prefix?: string | null;
        } | null;
      }
    | null;
};

export type InvitationsQueryVariables = Exact<{ [key: string]: never }>;

export type InvitationsQuery = {
  __typename?: "Query";
  invitations?: Array<{
    __typename?: "Invitation";
    id: string;
    owner_name: string;
    owner_email: string;
    organization: string;
    invite_assignments?: Array<{
      __typename?: "InvitationAssignment";
      id: string;
      scope_id: string;
      scope_name: string;
      scope_type: string;
      purpose: string;
    }> | null;
  } | null> | null;
};

export type UpdateInvitationMutationVariables = Exact<{
  invitationId: Scalars["String"]["input"];
  action: Scalars["String"]["input"];
}>;

export type UpdateInvitationMutation = { __typename?: "Mutation"; updateInvitation?: string | null };

export type OrganizationFeaturesQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
}>;

export type OrganizationFeaturesQuery = { __typename?: "Query"; organizationFeatures?: Record<string, unknown> | null };

export type OrganizationThemeSettingsQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
}>;

export type OrganizationThemeSettingsQuery = {
  __typename?: "Query";
  organizationThemeSettings?: Record<string, unknown> | null;
};

export type UpdateOrganizationThemeSettingsMutationVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  value: Scalars["JSONObject"]["input"];
}>;

export type UpdateOrganizationThemeSettingsMutation = {
  __typename?: "Mutation";
  updateOrganizationThemeSettings?: Record<string, unknown> | null;
};

export type OrganizationPerspectivesQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
}>;

export type OrganizationPerspectivesQuery = { __typename?: "Query"; organizationPerspectives?: Record<string, unknown> | null };

export type UpdateOrganizationPerspectivesMutationVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  value: Scalars["JSONObject"]["input"];
}>;

export type UpdateOrganizationPerspectivesMutation = {
  __typename?: "Mutation";
  updateOrganizationPerspectives?: Record<string, unknown> | null;
};

export type CreateDataSourceMutationVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  params: CreateDataSourceInput;
}>;

export type CreateDataSourceMutation = {
  __typename?: "Mutation";
  createDataSource?:
    | { __typename?: "AlibabaDataSource"; id: string; name: string }
    | { __typename?: "AwsDataSource"; id: string; name: string }
    | { __typename?: "AzureSubscriptionDataSource"; id: string; name: string }
    | { __typename?: "AzureTenantDataSource"; id: string; name: string }
    | { __typename?: "DatabricksDataSource"; id: string; name: string }
    | { __typename?: "EnvironmentDataSource"; id: string; name: string }
    | { __typename?: "GcpDataSource"; id: string; name: string }
    | { __typename?: "GcpTenantDataSource"; id: string; name: string }
    | { __typename?: "K8sDataSource"; id: string; name: string }
    | { __typename?: "NebiusDataSource"; id: string; name: string }
    | null;
};

export type EmployeeEmailsQueryVariables = Exact<{
  employeeId: Scalars["ID"]["input"];
}>;

export type EmployeeEmailsQuery = {
  __typename?: "Query";
  employeeEmails?: Array<{
    __typename?: "EmployeeEmail";
    id: string;
    employee_id: string;
    email_template: string;
    enabled: boolean;
    available_by_role: boolean;
  } | null> | null;
};

export type GetOrganizationConstraintQueryVariables = Exact<{
  constraintId: Scalars["ID"]["input"];
}>;

export type GetOrganizationConstraintQuery = {
  __typename?: "Query";
  organizationConstraint?: {
    __typename?: "OrganizationConstraint";
    id: string;
    name: string;
    type: OrganizationConstraintType;
    definition: Record<string, unknown>;
    filters: Record<string, unknown>;
    last_run_result: Record<string, unknown>;
  } | null;
};

export type UpdateEmployeeEmailsMutationVariables = Exact<{
  employeeId: Scalars["ID"]["input"];
  params: UpdateEmployeeEmailsInput;
}>;

export type UpdateEmployeeEmailsMutation = {
  __typename?: "Mutation";
  updateEmployeeEmails?: Array<{
    __typename?: "EmployeeEmail";
    id: string;
    employee_id: string;
    email_template: string;
    enabled: boolean;
    available_by_role: boolean;
  } | null> | null;
};

export type GetResourceCountBreakdownQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<BreakdownParams>;
}>;

export type GetResourceCountBreakdownQuery = {
  __typename?: "Query";
  resourceCountBreakdown?: {
    __typename?: "ResourceCountBreakdown";
    breakdown: Record<string, unknown>;
    counts: Record<string, unknown>;
    start_date: number;
    end_date: number;
  } | null;
};

export type MetaBreakdownQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<BreakdownParams>;
}>;

export type MetaBreakdownQuery = {
  __typename?: "Query";
  metaBreakdown?: {
    __typename?: "MetaBreakdown";
    breakdown: Record<string, unknown>;
    totals: Record<string, unknown>;
    start_date: number;
    end_date: number;
  } | null;
};

export type UpdateEmployeeEmailMutationVariables = Exact<{
  employeeId: Scalars["ID"]["input"];
  params: UpdateEmployeeEmailInput;
}>;

export type UpdateEmployeeEmailMutation = {
  __typename?: "Mutation";
  updateEmployeeEmail?: {
    __typename?: "EmployeeEmail";
    id: string;
    employee_id: string;
    email_template: string;
    enabled: boolean;
    available_by_role: boolean;
  } | null;
};

export type UpdateDataSourceMutationVariables = Exact<{
  dataSourceId: Scalars["ID"]["input"];
  params: UpdateDataSourceInput;
}>;

export type UpdateDataSourceMutation = {
  __typename?: "Mutation";
  updateDataSource?:
    | {
        __typename?: "AlibabaDataSource";
        id: string;
        name: string;
        config?: { __typename?: "AlibabaConfig"; access_key_id?: string | null } | null;
      }
    | {
        __typename?: "AwsDataSource";
        id: string;
        name: string;
        config?: {
          __typename?: "AwsConfig";
          assume_role_account_id?: string | null;
          assume_role_name?: string | null;
          access_key_id?: string | null;
          linked?: boolean | null;
          use_edp_discount?: boolean | null;
          cur_version?: number | null;
          bucket_name?: string | null;
          bucket_prefix?: string | null;
          config_scheme?: string | null;
          region_name?: string | null;
          report_name?: string | null;
        } | null;
      }
    | {
        __typename?: "AzureSubscriptionDataSource";
        id: string;
        name: string;
        config?: {
          __typename?: "AzureSubscriptionConfig";
          client_id?: string | null;
          expense_import_scheme?: string | null;
          subscription_id?: string | null;
          tenant?: string | null;
          export_name?: string | null;
          container?: string | null;
          directory?: string | null;
        } | null;
      }
    | {
        __typename?: "AzureTenantDataSource";
        id: string;
        name: string;
        config?: { __typename?: "AzureTenantConfig"; client_id?: string | null; tenant?: string | null } | null;
      }
    | {
        __typename?: "DatabricksDataSource";
        id: string;
        name: string;
        config?: { __typename?: "DatabricksConfig"; account_id?: string | null; client_id?: string | null } | null;
      }
    | { __typename?: "EnvironmentDataSource"; id: string; name: string }
    | {
        __typename?: "GcpDataSource";
        id: string;
        name: string;
        config?: {
          __typename?: "GcpConfig";
          billing_data?: {
            __typename?: "GcpBillingDataConfig";
            dataset_name: string;
            table_name: string;
            project_id?: string | null;
          } | null;
          pricing_data?: {
            __typename?: "GcpPricingDataConfig";
            dataset_name: string;
            table_name: string;
            project_id?: string | null;
          } | null;
        } | null;
      }
    | { __typename?: "GcpTenantDataSource"; id: string; name: string }
    | {
        __typename?: "K8sDataSource";
        id: string;
        name: string;
        config?: {
          __typename?: "K8sConfig";
          custom_price?: boolean | null;
          user?: string | null;
          cost_model?: { __typename?: "K8CostModelConfig"; cpu_hourly_cost: number; memory_hourly_cost: number } | null;
        } | null;
      }
    | {
        __typename?: "NebiusDataSource";
        id: string;
        name: string;
        config?: {
          __typename?: "NebiusConfig";
          cloud_name?: string | null;
          service_account_id?: string | null;
          key_id?: string | null;
          access_key_id?: string | null;
          bucket_name?: string | null;
          bucket_prefix?: string | null;
        } | null;
      }
    | null;
};

export type DeleteDataSourceMutationVariables = Exact<{
  dataSourceId: Scalars["ID"]["input"];
}>;

export type DeleteDataSourceMutation = { __typename?: "Mutation"; deleteDataSource?: string | null };

export type GetExpensesDailyBreakdownQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<BreakdownParams>;
}>;

export type GetExpensesDailyBreakdownQuery = {
  __typename?: "Query";
  expensesDailyBreakdown?: {
    __typename?: "ExpensesDailyBreakdown";
    breakdown: Record<string, unknown>;
    counts: Record<string, unknown>;
  } | null;
};

export type GetOrganizationLimitHitsQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  constraintId: Scalars["ID"]["input"];
}>;

export type GetOrganizationLimitHitsQuery = {
  __typename?: "Query";
  organizationLimitHits?: Array<{
    __typename?: "OrganizationLimitHit";
    run_result: Record<string, unknown>;
    created_at: number;
    value: number;
    constraint_limit: number;
  }> | null;
};

export type RelevantFlavorsQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  requestParams?: InputMaybe<Scalars["JSONObject"]["input"]>;
}>;

export type RelevantFlavorsQuery = { __typename?: "Query"; relevantFlavors?: Record<string, unknown> | null };

export type CleanExpensesQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<CleanExpensesParams>;
}>;

export type CleanExpensesQuery = { __typename?: "Query"; cleanExpenses?: Record<string, unknown> | null };

export type CloudPoliciesQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<CloudPoliciesParams>;
}>;

export type CloudPoliciesQuery = { __typename?: "Query"; cloudPolicies?: Record<string, unknown> | null };

export type AvailableFiltersQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  params?: InputMaybe<AvailableFiltersParams>;
}>;

export type AvailableFiltersQuery = { __typename?: "Query"; availableFilters?: Record<string, unknown> | null };

export const AwsDataSourceConfigFragmentFragmentDoc = gql`
  fragment AwsDataSourceConfigFragment on AwsDataSource {
    config {
      assume_role_account_id
      assume_role_name
      access_key_id
      linked
      use_edp_discount
      cur_version
      bucket_name
      bucket_prefix
      config_scheme
      region_name
      report_name
    }
  }
`;
export const AzureTenantDataSourceConfigFragmentFragmentDoc = gql`
  fragment AzureTenantDataSourceConfigFragment on AzureTenantDataSource {
    config {
      client_id
      tenant
    }
  }
`;
export const AzureSubscriptionDataSourceConfigFragmentFragmentDoc = gql`
  fragment AzureSubscriptionDataSourceConfigFragment on AzureSubscriptionDataSource {
    config {
      client_id
      expense_import_scheme
      subscription_id
      tenant
      export_name
      container
      directory
    }
  }
`;
export const GcpDataSourceConfigFragmentFragmentDoc = gql`
  fragment GcpDataSourceConfigFragment on GcpDataSource {
    config {
      billing_data {
        dataset_name
        table_name
        project_id
      }
      pricing_data {
        dataset_name
        table_name
        project_id
      }
    }
  }
`;
export const GcpTenantDataSourceConfigFragmentFragmentDoc = gql`
  fragment GcpTenantDataSourceConfigFragment on GcpTenantDataSource {
    config {
      billing_data {
        dataset_name
        table_name
        project_id
      }
      pricing_data {
        dataset_name
        table_name
        project_id
      }
    }
  }
`;
export const AlibabaDataSourceConfigFragmentFragmentDoc = gql`
  fragment AlibabaDataSourceConfigFragment on AlibabaDataSource {
    config {
      access_key_id
    }
  }
`;
export const NebiusDataSourceConfigFragmentFragmentDoc = gql`
  fragment NebiusDataSourceConfigFragment on NebiusDataSource {
    config {
      cloud_name
      service_account_id
      key_id
      access_key_id
      bucket_name
      bucket_prefix
    }
  }
`;
export const DatabricksDataSourceConfigFragmentFragmentDoc = gql`
  fragment DatabricksDataSourceConfigFragment on DatabricksDataSource {
    config {
      account_id
      client_id
    }
  }
`;
export const K8sDataSourceConfigFragmentFragmentDoc = gql`
  fragment K8sDataSourceConfigFragment on K8sDataSource {
    config {
      cost_model {
        cpu_hourly_cost
        memory_hourly_cost
      }
      custom_price
      user
    }
  }
`;
export const OrganizationsDocument = gql`
  query Organizations {
    organizations {
      id
      name
      pool_id
      currency
      is_demo
      disabled
    }
  }
`;

/**
 * __useOrganizationsQuery__
 *
 * To run a query within a React component, call `useOrganizationsQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationsQuery({
 *   variables: {
 *   },
 * });
 */
export function useOrganizationsQuery(baseOptions?: Apollo.QueryHookOptions<OrganizationsQuery, OrganizationsQueryVariables>) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<OrganizationsQuery, OrganizationsQueryVariables>(OrganizationsDocument, options);
}
export function useOrganizationsLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<OrganizationsQuery, OrganizationsQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<OrganizationsQuery, OrganizationsQueryVariables>(OrganizationsDocument, options);
}
export function useOrganizationsSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<OrganizationsQuery, OrganizationsQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<OrganizationsQuery, OrganizationsQueryVariables>(OrganizationsDocument, options);
}
export type OrganizationsQueryHookResult = ReturnType<typeof useOrganizationsQuery>;
export type OrganizationsLazyQueryHookResult = ReturnType<typeof useOrganizationsLazyQuery>;
export type OrganizationsSuspenseQueryHookResult = ReturnType<typeof useOrganizationsSuspenseQuery>;
export type OrganizationsQueryResult = Apollo.QueryResult<OrganizationsQuery, OrganizationsQueryVariables>;
export function refetchOrganizationsQuery(variables?: OrganizationsQueryVariables) {
  return { query: OrganizationsDocument, variables: variables };
}
export const CreateOrganizationDocument = gql`
  mutation CreateOrganization($organizationName: String!) {
    createOrganization(organizationName: $organizationName) {
      id
      name
    }
  }
`;
export type CreateOrganizationMutationFn = Apollo.MutationFunction<
  CreateOrganizationMutation,
  CreateOrganizationMutationVariables
>;

/**
 * __useCreateOrganizationMutation__
 *
 * To run a mutation, you first call `useCreateOrganizationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateOrganizationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createOrganizationMutation, { data, loading, error }] = useCreateOrganizationMutation({
 *   variables: {
 *      organizationName: // value for 'organizationName'
 *   },
 * });
 */
export function useCreateOrganizationMutation(
  baseOptions?: Apollo.MutationHookOptions<CreateOrganizationMutation, CreateOrganizationMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<CreateOrganizationMutation, CreateOrganizationMutationVariables>(
    CreateOrganizationDocument,
    options
  );
}
export type CreateOrganizationMutationHookResult = ReturnType<typeof useCreateOrganizationMutation>;
export type CreateOrganizationMutationResult = Apollo.MutationResult<CreateOrganizationMutation>;
export type CreateOrganizationMutationOptions = Apollo.BaseMutationOptions<
  CreateOrganizationMutation,
  CreateOrganizationMutationVariables
>;
export const UpdateOrganizationDocument = gql`
  mutation UpdateOrganization($organizationId: ID!, $params: UpdateOrganizationInput!) {
    updateOrganization(organizationId: $organizationId, params: $params) {
      id
      name
      currency
    }
  }
`;
export type UpdateOrganizationMutationFn = Apollo.MutationFunction<
  UpdateOrganizationMutation,
  UpdateOrganizationMutationVariables
>;

/**
 * __useUpdateOrganizationMutation__
 *
 * To run a mutation, you first call `useUpdateOrganizationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateOrganizationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateOrganizationMutation, { data, loading, error }] = useUpdateOrganizationMutation({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useUpdateOrganizationMutation(
  baseOptions?: Apollo.MutationHookOptions<UpdateOrganizationMutation, UpdateOrganizationMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<UpdateOrganizationMutation, UpdateOrganizationMutationVariables>(
    UpdateOrganizationDocument,
    options
  );
}
export type UpdateOrganizationMutationHookResult = ReturnType<typeof useUpdateOrganizationMutation>;
export type UpdateOrganizationMutationResult = Apollo.MutationResult<UpdateOrganizationMutation>;
export type UpdateOrganizationMutationOptions = Apollo.BaseMutationOptions<
  UpdateOrganizationMutation,
  UpdateOrganizationMutationVariables
>;
export const DeleteOrganizationDocument = gql`
  mutation DeleteOrganization($organizationId: ID!) {
    deleteOrganization(organizationId: $organizationId)
  }
`;
export type DeleteOrganizationMutationFn = Apollo.MutationFunction<
  DeleteOrganizationMutation,
  DeleteOrganizationMutationVariables
>;

/**
 * __useDeleteOrganizationMutation__
 *
 * To run a mutation, you first call `useDeleteOrganizationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteOrganizationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteOrganizationMutation, { data, loading, error }] = useDeleteOrganizationMutation({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *   },
 * });
 */
export function useDeleteOrganizationMutation(
  baseOptions?: Apollo.MutationHookOptions<DeleteOrganizationMutation, DeleteOrganizationMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<DeleteOrganizationMutation, DeleteOrganizationMutationVariables>(
    DeleteOrganizationDocument,
    options
  );
}
export type DeleteOrganizationMutationHookResult = ReturnType<typeof useDeleteOrganizationMutation>;
export type DeleteOrganizationMutationResult = Apollo.MutationResult<DeleteOrganizationMutation>;
export type DeleteOrganizationMutationOptions = Apollo.BaseMutationOptions<
  DeleteOrganizationMutation,
  DeleteOrganizationMutationVariables
>;
export const CurrentEmployeeDocument = gql`
  query CurrentEmployee($organizationId: ID!) {
    currentEmployee(organizationId: $organizationId) {
      id
      jira_connected
      slack_connected
    }
  }
`;

/**
 * __useCurrentEmployeeQuery__
 *
 * To run a query within a React component, call `useCurrentEmployeeQuery` and pass it any options that fit your needs.
 * When your component renders, `useCurrentEmployeeQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useCurrentEmployeeQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *   },
 * });
 */
export function useCurrentEmployeeQuery(
  baseOptions: Apollo.QueryHookOptions<CurrentEmployeeQuery, CurrentEmployeeQueryVariables> &
    ({ variables: CurrentEmployeeQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<CurrentEmployeeQuery, CurrentEmployeeQueryVariables>(CurrentEmployeeDocument, options);
}
export function useCurrentEmployeeLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<CurrentEmployeeQuery, CurrentEmployeeQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<CurrentEmployeeQuery, CurrentEmployeeQueryVariables>(CurrentEmployeeDocument, options);
}
export function useCurrentEmployeeSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<CurrentEmployeeQuery, CurrentEmployeeQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<CurrentEmployeeQuery, CurrentEmployeeQueryVariables>(CurrentEmployeeDocument, options);
}
export type CurrentEmployeeQueryHookResult = ReturnType<typeof useCurrentEmployeeQuery>;
export type CurrentEmployeeLazyQueryHookResult = ReturnType<typeof useCurrentEmployeeLazyQuery>;
export type CurrentEmployeeSuspenseQueryHookResult = ReturnType<typeof useCurrentEmployeeSuspenseQuery>;
export type CurrentEmployeeQueryResult = Apollo.QueryResult<CurrentEmployeeQuery, CurrentEmployeeQueryVariables>;
export function refetchCurrentEmployeeQuery(variables: CurrentEmployeeQueryVariables) {
  return { query: CurrentEmployeeDocument, variables: variables };
}
export const DataSourcesDocument = gql`
  query DataSources($organizationId: ID!) {
    dataSources(organizationId: $organizationId) {
      account_id
      created_at
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
        resources
        forecast
        last_month_cost
      }
      ...AwsDataSourceConfigFragment
      ...AzureTenantDataSourceConfigFragment
      ...AzureSubscriptionDataSourceConfigFragment
      ...GcpDataSourceConfigFragment
      ...GcpTenantDataSourceConfigFragment
      ...AlibabaDataSourceConfigFragment
      ...NebiusDataSourceConfigFragment
      ...DatabricksDataSourceConfigFragment
      ...K8sDataSourceConfigFragment
    }
  }
  ${AwsDataSourceConfigFragmentFragmentDoc}
  ${AzureTenantDataSourceConfigFragmentFragmentDoc}
  ${AzureSubscriptionDataSourceConfigFragmentFragmentDoc}
  ${GcpDataSourceConfigFragmentFragmentDoc}
  ${GcpTenantDataSourceConfigFragmentFragmentDoc}
  ${AlibabaDataSourceConfigFragmentFragmentDoc}
  ${NebiusDataSourceConfigFragmentFragmentDoc}
  ${DatabricksDataSourceConfigFragmentFragmentDoc}
  ${K8sDataSourceConfigFragmentFragmentDoc}
`;

/**
 * __useDataSourcesQuery__
 *
 * To run a query within a React component, call `useDataSourcesQuery` and pass it any options that fit your needs.
 * When your component renders, `useDataSourcesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useDataSourcesQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *   },
 * });
 */
export function useDataSourcesQuery(
  baseOptions: Apollo.QueryHookOptions<DataSourcesQuery, DataSourcesQueryVariables> &
    ({ variables: DataSourcesQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<DataSourcesQuery, DataSourcesQueryVariables>(DataSourcesDocument, options);
}
export function useDataSourcesLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<DataSourcesQuery, DataSourcesQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<DataSourcesQuery, DataSourcesQueryVariables>(DataSourcesDocument, options);
}
export function useDataSourcesSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<DataSourcesQuery, DataSourcesQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<DataSourcesQuery, DataSourcesQueryVariables>(DataSourcesDocument, options);
}
export type DataSourcesQueryHookResult = ReturnType<typeof useDataSourcesQuery>;
export type DataSourcesLazyQueryHookResult = ReturnType<typeof useDataSourcesLazyQuery>;
export type DataSourcesSuspenseQueryHookResult = ReturnType<typeof useDataSourcesSuspenseQuery>;
export type DataSourcesQueryResult = Apollo.QueryResult<DataSourcesQuery, DataSourcesQueryVariables>;
export function refetchDataSourcesQuery(variables: DataSourcesQueryVariables) {
  return { query: DataSourcesDocument, variables: variables };
}
export const DataSourceDocument = gql`
  query DataSource($dataSourceId: ID!, $requestParams: DataSourceRequestParams) {
    dataSource(dataSourceId: $dataSourceId, requestParams: $requestParams) {
      account_id
      created_at
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
      ...AwsDataSourceConfigFragment
      ...AzureTenantDataSourceConfigFragment
      ...AzureSubscriptionDataSourceConfigFragment
      ...GcpDataSourceConfigFragment
      ...GcpTenantDataSourceConfigFragment
      ...AlibabaDataSourceConfigFragment
      ...NebiusDataSourceConfigFragment
      ...DatabricksDataSourceConfigFragment
      ...K8sDataSourceConfigFragment
    }
  }
  ${AwsDataSourceConfigFragmentFragmentDoc}
  ${AzureTenantDataSourceConfigFragmentFragmentDoc}
  ${AzureSubscriptionDataSourceConfigFragmentFragmentDoc}
  ${GcpDataSourceConfigFragmentFragmentDoc}
  ${GcpTenantDataSourceConfigFragmentFragmentDoc}
  ${AlibabaDataSourceConfigFragmentFragmentDoc}
  ${NebiusDataSourceConfigFragmentFragmentDoc}
  ${DatabricksDataSourceConfigFragmentFragmentDoc}
  ${K8sDataSourceConfigFragmentFragmentDoc}
`;

/**
 * __useDataSourceQuery__
 *
 * To run a query within a React component, call `useDataSourceQuery` and pass it any options that fit your needs.
 * When your component renders, `useDataSourceQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useDataSourceQuery({
 *   variables: {
 *      dataSourceId: // value for 'dataSourceId'
 *      requestParams: // value for 'requestParams'
 *   },
 * });
 */
export function useDataSourceQuery(
  baseOptions: Apollo.QueryHookOptions<DataSourceQuery, DataSourceQueryVariables> &
    ({ variables: DataSourceQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<DataSourceQuery, DataSourceQueryVariables>(DataSourceDocument, options);
}
export function useDataSourceLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<DataSourceQuery, DataSourceQueryVariables>) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<DataSourceQuery, DataSourceQueryVariables>(DataSourceDocument, options);
}
export function useDataSourceSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<DataSourceQuery, DataSourceQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<DataSourceQuery, DataSourceQueryVariables>(DataSourceDocument, options);
}
export type DataSourceQueryHookResult = ReturnType<typeof useDataSourceQuery>;
export type DataSourceLazyQueryHookResult = ReturnType<typeof useDataSourceLazyQuery>;
export type DataSourceSuspenseQueryHookResult = ReturnType<typeof useDataSourceSuspenseQuery>;
export type DataSourceQueryResult = Apollo.QueryResult<DataSourceQuery, DataSourceQueryVariables>;
export function refetchDataSourceQuery(variables: DataSourceQueryVariables) {
  return { query: DataSourceDocument, variables: variables };
}
export const InvitationsDocument = gql`
  query Invitations {
    invitations {
      id
      owner_name
      owner_email
      organization
      invite_assignments {
        id
        scope_id
        scope_name
        scope_type
        purpose
      }
    }
  }
`;

/**
 * __useInvitationsQuery__
 *
 * To run a query within a React component, call `useInvitationsQuery` and pass it any options that fit your needs.
 * When your component renders, `useInvitationsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useInvitationsQuery({
 *   variables: {
 *   },
 * });
 */
export function useInvitationsQuery(baseOptions?: Apollo.QueryHookOptions<InvitationsQuery, InvitationsQueryVariables>) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<InvitationsQuery, InvitationsQueryVariables>(InvitationsDocument, options);
}
export function useInvitationsLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<InvitationsQuery, InvitationsQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<InvitationsQuery, InvitationsQueryVariables>(InvitationsDocument, options);
}
export function useInvitationsSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<InvitationsQuery, InvitationsQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<InvitationsQuery, InvitationsQueryVariables>(InvitationsDocument, options);
}
export type InvitationsQueryHookResult = ReturnType<typeof useInvitationsQuery>;
export type InvitationsLazyQueryHookResult = ReturnType<typeof useInvitationsLazyQuery>;
export type InvitationsSuspenseQueryHookResult = ReturnType<typeof useInvitationsSuspenseQuery>;
export type InvitationsQueryResult = Apollo.QueryResult<InvitationsQuery, InvitationsQueryVariables>;
export function refetchInvitationsQuery(variables?: InvitationsQueryVariables) {
  return { query: InvitationsDocument, variables: variables };
}
export const UpdateInvitationDocument = gql`
  mutation UpdateInvitation($invitationId: String!, $action: String!) {
    updateInvitation(invitationId: $invitationId, action: $action)
  }
`;
export type UpdateInvitationMutationFn = Apollo.MutationFunction<UpdateInvitationMutation, UpdateInvitationMutationVariables>;

/**
 * __useUpdateInvitationMutation__
 *
 * To run a mutation, you first call `useUpdateInvitationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateInvitationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateInvitationMutation, { data, loading, error }] = useUpdateInvitationMutation({
 *   variables: {
 *      invitationId: // value for 'invitationId'
 *      action: // value for 'action'
 *   },
 * });
 */
export function useUpdateInvitationMutation(
  baseOptions?: Apollo.MutationHookOptions<UpdateInvitationMutation, UpdateInvitationMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<UpdateInvitationMutation, UpdateInvitationMutationVariables>(UpdateInvitationDocument, options);
}
export type UpdateInvitationMutationHookResult = ReturnType<typeof useUpdateInvitationMutation>;
export type UpdateInvitationMutationResult = Apollo.MutationResult<UpdateInvitationMutation>;
export type UpdateInvitationMutationOptions = Apollo.BaseMutationOptions<
  UpdateInvitationMutation,
  UpdateInvitationMutationVariables
>;
export const OrganizationFeaturesDocument = gql`
  query OrganizationFeatures($organizationId: ID!) {
    organizationFeatures(organizationId: $organizationId)
  }
`;

/**
 * __useOrganizationFeaturesQuery__
 *
 * To run a query within a React component, call `useOrganizationFeaturesQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationFeaturesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationFeaturesQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *   },
 * });
 */
export function useOrganizationFeaturesQuery(
  baseOptions: Apollo.QueryHookOptions<OrganizationFeaturesQuery, OrganizationFeaturesQueryVariables> &
    ({ variables: OrganizationFeaturesQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<OrganizationFeaturesQuery, OrganizationFeaturesQueryVariables>(OrganizationFeaturesDocument, options);
}
export function useOrganizationFeaturesLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<OrganizationFeaturesQuery, OrganizationFeaturesQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<OrganizationFeaturesQuery, OrganizationFeaturesQueryVariables>(
    OrganizationFeaturesDocument,
    options
  );
}
export function useOrganizationFeaturesSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<OrganizationFeaturesQuery, OrganizationFeaturesQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<OrganizationFeaturesQuery, OrganizationFeaturesQueryVariables>(
    OrganizationFeaturesDocument,
    options
  );
}
export type OrganizationFeaturesQueryHookResult = ReturnType<typeof useOrganizationFeaturesQuery>;
export type OrganizationFeaturesLazyQueryHookResult = ReturnType<typeof useOrganizationFeaturesLazyQuery>;
export type OrganizationFeaturesSuspenseQueryHookResult = ReturnType<typeof useOrganizationFeaturesSuspenseQuery>;
export type OrganizationFeaturesQueryResult = Apollo.QueryResult<OrganizationFeaturesQuery, OrganizationFeaturesQueryVariables>;
export function refetchOrganizationFeaturesQuery(variables: OrganizationFeaturesQueryVariables) {
  return { query: OrganizationFeaturesDocument, variables: variables };
}
export const OrganizationThemeSettingsDocument = gql`
  query OrganizationThemeSettings($organizationId: ID!) {
    organizationThemeSettings(organizationId: $organizationId)
  }
`;

/**
 * __useOrganizationThemeSettingsQuery__
 *
 * To run a query within a React component, call `useOrganizationThemeSettingsQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationThemeSettingsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationThemeSettingsQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *   },
 * });
 */
export function useOrganizationThemeSettingsQuery(
  baseOptions: Apollo.QueryHookOptions<OrganizationThemeSettingsQuery, OrganizationThemeSettingsQueryVariables> &
    ({ variables: OrganizationThemeSettingsQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<OrganizationThemeSettingsQuery, OrganizationThemeSettingsQueryVariables>(
    OrganizationThemeSettingsDocument,
    options
  );
}
export function useOrganizationThemeSettingsLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<OrganizationThemeSettingsQuery, OrganizationThemeSettingsQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<OrganizationThemeSettingsQuery, OrganizationThemeSettingsQueryVariables>(
    OrganizationThemeSettingsDocument,
    options
  );
}
export function useOrganizationThemeSettingsSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<OrganizationThemeSettingsQuery, OrganizationThemeSettingsQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<OrganizationThemeSettingsQuery, OrganizationThemeSettingsQueryVariables>(
    OrganizationThemeSettingsDocument,
    options
  );
}
export type OrganizationThemeSettingsQueryHookResult = ReturnType<typeof useOrganizationThemeSettingsQuery>;
export type OrganizationThemeSettingsLazyQueryHookResult = ReturnType<typeof useOrganizationThemeSettingsLazyQuery>;
export type OrganizationThemeSettingsSuspenseQueryHookResult = ReturnType<typeof useOrganizationThemeSettingsSuspenseQuery>;
export type OrganizationThemeSettingsQueryResult = Apollo.QueryResult<
  OrganizationThemeSettingsQuery,
  OrganizationThemeSettingsQueryVariables
>;
export function refetchOrganizationThemeSettingsQuery(variables: OrganizationThemeSettingsQueryVariables) {
  return { query: OrganizationThemeSettingsDocument, variables: variables };
}
export const UpdateOrganizationThemeSettingsDocument = gql`
  mutation UpdateOrganizationThemeSettings($organizationId: ID!, $value: JSONObject!) {
    updateOrganizationThemeSettings(organizationId: $organizationId, value: $value)
  }
`;
export type UpdateOrganizationThemeSettingsMutationFn = Apollo.MutationFunction<
  UpdateOrganizationThemeSettingsMutation,
  UpdateOrganizationThemeSettingsMutationVariables
>;

/**
 * __useUpdateOrganizationThemeSettingsMutation__
 *
 * To run a mutation, you first call `useUpdateOrganizationThemeSettingsMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateOrganizationThemeSettingsMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateOrganizationThemeSettingsMutation, { data, loading, error }] = useUpdateOrganizationThemeSettingsMutation({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      value: // value for 'value'
 *   },
 * });
 */
export function useUpdateOrganizationThemeSettingsMutation(
  baseOptions?: Apollo.MutationHookOptions<
    UpdateOrganizationThemeSettingsMutation,
    UpdateOrganizationThemeSettingsMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<UpdateOrganizationThemeSettingsMutation, UpdateOrganizationThemeSettingsMutationVariables>(
    UpdateOrganizationThemeSettingsDocument,
    options
  );
}
export type UpdateOrganizationThemeSettingsMutationHookResult = ReturnType<typeof useUpdateOrganizationThemeSettingsMutation>;
export type UpdateOrganizationThemeSettingsMutationResult = Apollo.MutationResult<UpdateOrganizationThemeSettingsMutation>;
export type UpdateOrganizationThemeSettingsMutationOptions = Apollo.BaseMutationOptions<
  UpdateOrganizationThemeSettingsMutation,
  UpdateOrganizationThemeSettingsMutationVariables
>;
export const OrganizationPerspectivesDocument = gql`
  query OrganizationPerspectives($organizationId: ID!) {
    organizationPerspectives(organizationId: $organizationId)
  }
`;

/**
 * __useOrganizationPerspectivesQuery__
 *
 * To run a query within a React component, call `useOrganizationPerspectivesQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationPerspectivesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationPerspectivesQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *   },
 * });
 */
export function useOrganizationPerspectivesQuery(
  baseOptions: Apollo.QueryHookOptions<OrganizationPerspectivesQuery, OrganizationPerspectivesQueryVariables> &
    ({ variables: OrganizationPerspectivesQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<OrganizationPerspectivesQuery, OrganizationPerspectivesQueryVariables>(
    OrganizationPerspectivesDocument,
    options
  );
}
export function useOrganizationPerspectivesLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<OrganizationPerspectivesQuery, OrganizationPerspectivesQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<OrganizationPerspectivesQuery, OrganizationPerspectivesQueryVariables>(
    OrganizationPerspectivesDocument,
    options
  );
}
export function useOrganizationPerspectivesSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<OrganizationPerspectivesQuery, OrganizationPerspectivesQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<OrganizationPerspectivesQuery, OrganizationPerspectivesQueryVariables>(
    OrganizationPerspectivesDocument,
    options
  );
}
export type OrganizationPerspectivesQueryHookResult = ReturnType<typeof useOrganizationPerspectivesQuery>;
export type OrganizationPerspectivesLazyQueryHookResult = ReturnType<typeof useOrganizationPerspectivesLazyQuery>;
export type OrganizationPerspectivesSuspenseQueryHookResult = ReturnType<typeof useOrganizationPerspectivesSuspenseQuery>;
export type OrganizationPerspectivesQueryResult = Apollo.QueryResult<
  OrganizationPerspectivesQuery,
  OrganizationPerspectivesQueryVariables
>;
export function refetchOrganizationPerspectivesQuery(variables: OrganizationPerspectivesQueryVariables) {
  return { query: OrganizationPerspectivesDocument, variables: variables };
}
export const UpdateOrganizationPerspectivesDocument = gql`
  mutation UpdateOrganizationPerspectives($organizationId: ID!, $value: JSONObject!) {
    updateOrganizationPerspectives(organizationId: $organizationId, value: $value)
  }
`;
export type UpdateOrganizationPerspectivesMutationFn = Apollo.MutationFunction<
  UpdateOrganizationPerspectivesMutation,
  UpdateOrganizationPerspectivesMutationVariables
>;

/**
 * __useUpdateOrganizationPerspectivesMutation__
 *
 * To run a mutation, you first call `useUpdateOrganizationPerspectivesMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateOrganizationPerspectivesMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateOrganizationPerspectivesMutation, { data, loading, error }] = useUpdateOrganizationPerspectivesMutation({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      value: // value for 'value'
 *   },
 * });
 */
export function useUpdateOrganizationPerspectivesMutation(
  baseOptions?: Apollo.MutationHookOptions<
    UpdateOrganizationPerspectivesMutation,
    UpdateOrganizationPerspectivesMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<UpdateOrganizationPerspectivesMutation, UpdateOrganizationPerspectivesMutationVariables>(
    UpdateOrganizationPerspectivesDocument,
    options
  );
}
export type UpdateOrganizationPerspectivesMutationHookResult = ReturnType<typeof useUpdateOrganizationPerspectivesMutation>;
export type UpdateOrganizationPerspectivesMutationResult = Apollo.MutationResult<UpdateOrganizationPerspectivesMutation>;
export type UpdateOrganizationPerspectivesMutationOptions = Apollo.BaseMutationOptions<
  UpdateOrganizationPerspectivesMutation,
  UpdateOrganizationPerspectivesMutationVariables
>;
export const CreateDataSourceDocument = gql`
  mutation CreateDataSource($organizationId: ID!, $params: CreateDataSourceInput!) {
    createDataSource(organizationId: $organizationId, params: $params) {
      id
      name
    }
  }
`;
export type CreateDataSourceMutationFn = Apollo.MutationFunction<CreateDataSourceMutation, CreateDataSourceMutationVariables>;

/**
 * __useCreateDataSourceMutation__
 *
 * To run a mutation, you first call `useCreateDataSourceMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateDataSourceMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createDataSourceMutation, { data, loading, error }] = useCreateDataSourceMutation({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useCreateDataSourceMutation(
  baseOptions?: Apollo.MutationHookOptions<CreateDataSourceMutation, CreateDataSourceMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<CreateDataSourceMutation, CreateDataSourceMutationVariables>(CreateDataSourceDocument, options);
}
export type CreateDataSourceMutationHookResult = ReturnType<typeof useCreateDataSourceMutation>;
export type CreateDataSourceMutationResult = Apollo.MutationResult<CreateDataSourceMutation>;
export type CreateDataSourceMutationOptions = Apollo.BaseMutationOptions<
  CreateDataSourceMutation,
  CreateDataSourceMutationVariables
>;
export const EmployeeEmailsDocument = gql`
  query EmployeeEmails($employeeId: ID!) {
    employeeEmails(employeeId: $employeeId) {
      id
      employee_id
      email_template
      enabled
      available_by_role
    }
  }
`;

/**
 * __useEmployeeEmailsQuery__
 *
 * To run a query within a React component, call `useEmployeeEmailsQuery` and pass it any options that fit your needs.
 * When your component renders, `useEmployeeEmailsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useEmployeeEmailsQuery({
 *   variables: {
 *      employeeId: // value for 'employeeId'
 *   },
 * });
 */
export function useEmployeeEmailsQuery(
  baseOptions: Apollo.QueryHookOptions<EmployeeEmailsQuery, EmployeeEmailsQueryVariables> &
    ({ variables: EmployeeEmailsQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<EmployeeEmailsQuery, EmployeeEmailsQueryVariables>(EmployeeEmailsDocument, options);
}
export function useEmployeeEmailsLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<EmployeeEmailsQuery, EmployeeEmailsQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<EmployeeEmailsQuery, EmployeeEmailsQueryVariables>(EmployeeEmailsDocument, options);
}
export function useEmployeeEmailsSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<EmployeeEmailsQuery, EmployeeEmailsQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<EmployeeEmailsQuery, EmployeeEmailsQueryVariables>(EmployeeEmailsDocument, options);
}
export type EmployeeEmailsQueryHookResult = ReturnType<typeof useEmployeeEmailsQuery>;
export type EmployeeEmailsLazyQueryHookResult = ReturnType<typeof useEmployeeEmailsLazyQuery>;
export type EmployeeEmailsSuspenseQueryHookResult = ReturnType<typeof useEmployeeEmailsSuspenseQuery>;
export type EmployeeEmailsQueryResult = Apollo.QueryResult<EmployeeEmailsQuery, EmployeeEmailsQueryVariables>;
export function refetchEmployeeEmailsQuery(variables: EmployeeEmailsQueryVariables) {
  return { query: EmployeeEmailsDocument, variables: variables };
}
export const GetOrganizationConstraintDocument = gql`
  query GetOrganizationConstraint($constraintId: ID!) {
    organizationConstraint(constraintId: $constraintId) {
      id
      name
      type
      definition
      filters
      last_run_result
    }
  }
`;

/**
 * __useGetOrganizationConstraintQuery__
 *
 * To run a query within a React component, call `useGetOrganizationConstraintQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetOrganizationConstraintQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetOrganizationConstraintQuery({
 *   variables: {
 *      constraintId: // value for 'constraintId'
 *   },
 * });
 */
export function useGetOrganizationConstraintQuery(
  baseOptions: Apollo.QueryHookOptions<GetOrganizationConstraintQuery, GetOrganizationConstraintQueryVariables> &
    ({ variables: GetOrganizationConstraintQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetOrganizationConstraintQuery, GetOrganizationConstraintQueryVariables>(
    GetOrganizationConstraintDocument,
    options
  );
}
export function useGetOrganizationConstraintLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<GetOrganizationConstraintQuery, GetOrganizationConstraintQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetOrganizationConstraintQuery, GetOrganizationConstraintQueryVariables>(
    GetOrganizationConstraintDocument,
    options
  );
}
export function useGetOrganizationConstraintSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<GetOrganizationConstraintQuery, GetOrganizationConstraintQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<GetOrganizationConstraintQuery, GetOrganizationConstraintQueryVariables>(
    GetOrganizationConstraintDocument,
    options
  );
}
export type GetOrganizationConstraintQueryHookResult = ReturnType<typeof useGetOrganizationConstraintQuery>;
export type GetOrganizationConstraintLazyQueryHookResult = ReturnType<typeof useGetOrganizationConstraintLazyQuery>;
export type GetOrganizationConstraintSuspenseQueryHookResult = ReturnType<typeof useGetOrganizationConstraintSuspenseQuery>;
export type GetOrganizationConstraintQueryResult = Apollo.QueryResult<
  GetOrganizationConstraintQuery,
  GetOrganizationConstraintQueryVariables
>;
export function refetchGetOrganizationConstraintQuery(variables: GetOrganizationConstraintQueryVariables) {
  return { query: GetOrganizationConstraintDocument, variables: variables };
}
export const UpdateEmployeeEmailsDocument = gql`
  mutation UpdateEmployeeEmails($employeeId: ID!, $params: UpdateEmployeeEmailsInput!) {
    updateEmployeeEmails(employeeId: $employeeId, params: $params) {
      id
      employee_id
      email_template
      enabled
      available_by_role
    }
  }
`;
export type UpdateEmployeeEmailsMutationFn = Apollo.MutationFunction<
  UpdateEmployeeEmailsMutation,
  UpdateEmployeeEmailsMutationVariables
>;

/**
 * __useUpdateEmployeeEmailsMutation__
 *
 * To run a mutation, you first call `useUpdateEmployeeEmailsMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateEmployeeEmailsMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateEmployeeEmailsMutation, { data, loading, error }] = useUpdateEmployeeEmailsMutation({
 *   variables: {
 *      employeeId: // value for 'employeeId'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useUpdateEmployeeEmailsMutation(
  baseOptions?: Apollo.MutationHookOptions<UpdateEmployeeEmailsMutation, UpdateEmployeeEmailsMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<UpdateEmployeeEmailsMutation, UpdateEmployeeEmailsMutationVariables>(
    UpdateEmployeeEmailsDocument,
    options
  );
}
export type UpdateEmployeeEmailsMutationHookResult = ReturnType<typeof useUpdateEmployeeEmailsMutation>;
export type UpdateEmployeeEmailsMutationResult = Apollo.MutationResult<UpdateEmployeeEmailsMutation>;
export type UpdateEmployeeEmailsMutationOptions = Apollo.BaseMutationOptions<
  UpdateEmployeeEmailsMutation,
  UpdateEmployeeEmailsMutationVariables
>;
export const GetResourceCountBreakdownDocument = gql`
  query GetResourceCountBreakdown($organizationId: ID!, $params: BreakdownParams) {
    resourceCountBreakdown(organizationId: $organizationId, params: $params) {
      breakdown
      counts
      start_date
      end_date
    }
  }
`;

/**
 * __useGetResourceCountBreakdownQuery__
 *
 * To run a query within a React component, call `useGetResourceCountBreakdownQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetResourceCountBreakdownQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetResourceCountBreakdownQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useGetResourceCountBreakdownQuery(
  baseOptions: Apollo.QueryHookOptions<GetResourceCountBreakdownQuery, GetResourceCountBreakdownQueryVariables> &
    ({ variables: GetResourceCountBreakdownQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetResourceCountBreakdownQuery, GetResourceCountBreakdownQueryVariables>(
    GetResourceCountBreakdownDocument,
    options
  );
}
export function useGetResourceCountBreakdownLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<GetResourceCountBreakdownQuery, GetResourceCountBreakdownQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetResourceCountBreakdownQuery, GetResourceCountBreakdownQueryVariables>(
    GetResourceCountBreakdownDocument,
    options
  );
}
export function useGetResourceCountBreakdownSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<GetResourceCountBreakdownQuery, GetResourceCountBreakdownQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<GetResourceCountBreakdownQuery, GetResourceCountBreakdownQueryVariables>(
    GetResourceCountBreakdownDocument,
    options
  );
}
export type GetResourceCountBreakdownQueryHookResult = ReturnType<typeof useGetResourceCountBreakdownQuery>;
export type GetResourceCountBreakdownLazyQueryHookResult = ReturnType<typeof useGetResourceCountBreakdownLazyQuery>;
export type GetResourceCountBreakdownSuspenseQueryHookResult = ReturnType<typeof useGetResourceCountBreakdownSuspenseQuery>;
export type GetResourceCountBreakdownQueryResult = Apollo.QueryResult<
  GetResourceCountBreakdownQuery,
  GetResourceCountBreakdownQueryVariables
>;
export function refetchGetResourceCountBreakdownQuery(variables: GetResourceCountBreakdownQueryVariables) {
  return { query: GetResourceCountBreakdownDocument, variables: variables };
}
export const MetaBreakdownDocument = gql`
  query MetaBreakdown($organizationId: ID!, $params: BreakdownParams) {
    metaBreakdown(organizationId: $organizationId, params: $params) {
      breakdown
      totals
      start_date
      end_date
    }
  }
`;

/**
 * __useMetaBreakdownQuery__
 *
 * To run a query within a React component, call `useMetaBreakdownQuery` and pass it any options that fit your needs.
 * When your component renders, `useMetaBreakdownQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useMetaBreakdownQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useMetaBreakdownQuery(
  baseOptions: Apollo.QueryHookOptions<MetaBreakdownQuery, MetaBreakdownQueryVariables> &
    ({ variables: MetaBreakdownQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<MetaBreakdownQuery, MetaBreakdownQueryVariables>(MetaBreakdownDocument, options);
}
export function useMetaBreakdownLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<MetaBreakdownQuery, MetaBreakdownQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<MetaBreakdownQuery, MetaBreakdownQueryVariables>(MetaBreakdownDocument, options);
}
export function useMetaBreakdownSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<MetaBreakdownQuery, MetaBreakdownQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<MetaBreakdownQuery, MetaBreakdownQueryVariables>(MetaBreakdownDocument, options);
}
export type MetaBreakdownQueryHookResult = ReturnType<typeof useMetaBreakdownQuery>;
export type MetaBreakdownLazyQueryHookResult = ReturnType<typeof useMetaBreakdownLazyQuery>;
export type MetaBreakdownSuspenseQueryHookResult = ReturnType<typeof useMetaBreakdownSuspenseQuery>;
export type MetaBreakdownQueryResult = Apollo.QueryResult<MetaBreakdownQuery, MetaBreakdownQueryVariables>;
export function refetchMetaBreakdownQuery(variables: MetaBreakdownQueryVariables) {
  return { query: MetaBreakdownDocument, variables: variables };
}
export const UpdateEmployeeEmailDocument = gql`
  mutation UpdateEmployeeEmail($employeeId: ID!, $params: UpdateEmployeeEmailInput!) {
    updateEmployeeEmail(employeeId: $employeeId, params: $params) {
      id
      employee_id
      email_template
      enabled
      available_by_role
    }
  }
`;
export type UpdateEmployeeEmailMutationFn = Apollo.MutationFunction<
  UpdateEmployeeEmailMutation,
  UpdateEmployeeEmailMutationVariables
>;

/**
 * __useUpdateEmployeeEmailMutation__
 *
 * To run a mutation, you first call `useUpdateEmployeeEmailMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateEmployeeEmailMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateEmployeeEmailMutation, { data, loading, error }] = useUpdateEmployeeEmailMutation({
 *   variables: {
 *      employeeId: // value for 'employeeId'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useUpdateEmployeeEmailMutation(
  baseOptions?: Apollo.MutationHookOptions<UpdateEmployeeEmailMutation, UpdateEmployeeEmailMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<UpdateEmployeeEmailMutation, UpdateEmployeeEmailMutationVariables>(
    UpdateEmployeeEmailDocument,
    options
  );
}
export type UpdateEmployeeEmailMutationHookResult = ReturnType<typeof useUpdateEmployeeEmailMutation>;
export type UpdateEmployeeEmailMutationResult = Apollo.MutationResult<UpdateEmployeeEmailMutation>;
export type UpdateEmployeeEmailMutationOptions = Apollo.BaseMutationOptions<
  UpdateEmployeeEmailMutation,
  UpdateEmployeeEmailMutationVariables
>;
export const UpdateDataSourceDocument = gql`
  mutation UpdateDataSource($dataSourceId: ID!, $params: UpdateDataSourceInput!) {
    updateDataSource(dataSourceId: $dataSourceId, params: $params) {
      id
      name
      ...AwsDataSourceConfigFragment
      ...AzureTenantDataSourceConfigFragment
      ...AzureSubscriptionDataSourceConfigFragment
      ...GcpDataSourceConfigFragment
      ...AlibabaDataSourceConfigFragment
      ...NebiusDataSourceConfigFragment
      ...DatabricksDataSourceConfigFragment
      ...K8sDataSourceConfigFragment
    }
  }
  ${AwsDataSourceConfigFragmentFragmentDoc}
  ${AzureTenantDataSourceConfigFragmentFragmentDoc}
  ${AzureSubscriptionDataSourceConfigFragmentFragmentDoc}
  ${GcpDataSourceConfigFragmentFragmentDoc}
  ${AlibabaDataSourceConfigFragmentFragmentDoc}
  ${NebiusDataSourceConfigFragmentFragmentDoc}
  ${DatabricksDataSourceConfigFragmentFragmentDoc}
  ${K8sDataSourceConfigFragmentFragmentDoc}
`;
export type UpdateDataSourceMutationFn = Apollo.MutationFunction<UpdateDataSourceMutation, UpdateDataSourceMutationVariables>;

/**
 * __useUpdateDataSourceMutation__
 *
 * To run a mutation, you first call `useUpdateDataSourceMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateDataSourceMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateDataSourceMutation, { data, loading, error }] = useUpdateDataSourceMutation({
 *   variables: {
 *      dataSourceId: // value for 'dataSourceId'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useUpdateDataSourceMutation(
  baseOptions?: Apollo.MutationHookOptions<UpdateDataSourceMutation, UpdateDataSourceMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<UpdateDataSourceMutation, UpdateDataSourceMutationVariables>(UpdateDataSourceDocument, options);
}
export type UpdateDataSourceMutationHookResult = ReturnType<typeof useUpdateDataSourceMutation>;
export type UpdateDataSourceMutationResult = Apollo.MutationResult<UpdateDataSourceMutation>;
export type UpdateDataSourceMutationOptions = Apollo.BaseMutationOptions<
  UpdateDataSourceMutation,
  UpdateDataSourceMutationVariables
>;
export const DeleteDataSourceDocument = gql`
  mutation DeleteDataSource($dataSourceId: ID!) {
    deleteDataSource(dataSourceId: $dataSourceId)
  }
`;
export type DeleteDataSourceMutationFn = Apollo.MutationFunction<DeleteDataSourceMutation, DeleteDataSourceMutationVariables>;

/**
 * __useDeleteDataSourceMutation__
 *
 * To run a mutation, you first call `useDeleteDataSourceMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteDataSourceMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteDataSourceMutation, { data, loading, error }] = useDeleteDataSourceMutation({
 *   variables: {
 *      dataSourceId: // value for 'dataSourceId'
 *   },
 * });
 */
export function useDeleteDataSourceMutation(
  baseOptions?: Apollo.MutationHookOptions<DeleteDataSourceMutation, DeleteDataSourceMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<DeleteDataSourceMutation, DeleteDataSourceMutationVariables>(DeleteDataSourceDocument, options);
}
export type DeleteDataSourceMutationHookResult = ReturnType<typeof useDeleteDataSourceMutation>;
export type DeleteDataSourceMutationResult = Apollo.MutationResult<DeleteDataSourceMutation>;
export type DeleteDataSourceMutationOptions = Apollo.BaseMutationOptions<
  DeleteDataSourceMutation,
  DeleteDataSourceMutationVariables
>;
export const GetExpensesDailyBreakdownDocument = gql`
  query GetExpensesDailyBreakdown($organizationId: ID!, $params: BreakdownParams) {
    expensesDailyBreakdown(organizationId: $organizationId, params: $params) {
      breakdown
      counts
    }
  }
`;

/**
 * __useGetExpensesDailyBreakdownQuery__
 *
 * To run a query within a React component, call `useGetExpensesDailyBreakdownQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetExpensesDailyBreakdownQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetExpensesDailyBreakdownQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useGetExpensesDailyBreakdownQuery(
  baseOptions: Apollo.QueryHookOptions<GetExpensesDailyBreakdownQuery, GetExpensesDailyBreakdownQueryVariables> &
    ({ variables: GetExpensesDailyBreakdownQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetExpensesDailyBreakdownQuery, GetExpensesDailyBreakdownQueryVariables>(
    GetExpensesDailyBreakdownDocument,
    options
  );
}
export function useGetExpensesDailyBreakdownLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<GetExpensesDailyBreakdownQuery, GetExpensesDailyBreakdownQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetExpensesDailyBreakdownQuery, GetExpensesDailyBreakdownQueryVariables>(
    GetExpensesDailyBreakdownDocument,
    options
  );
}
export function useGetExpensesDailyBreakdownSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<GetExpensesDailyBreakdownQuery, GetExpensesDailyBreakdownQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<GetExpensesDailyBreakdownQuery, GetExpensesDailyBreakdownQueryVariables>(
    GetExpensesDailyBreakdownDocument,
    options
  );
}
export type GetExpensesDailyBreakdownQueryHookResult = ReturnType<typeof useGetExpensesDailyBreakdownQuery>;
export type GetExpensesDailyBreakdownLazyQueryHookResult = ReturnType<typeof useGetExpensesDailyBreakdownLazyQuery>;
export type GetExpensesDailyBreakdownSuspenseQueryHookResult = ReturnType<typeof useGetExpensesDailyBreakdownSuspenseQuery>;
export type GetExpensesDailyBreakdownQueryResult = Apollo.QueryResult<
  GetExpensesDailyBreakdownQuery,
  GetExpensesDailyBreakdownQueryVariables
>;
export function refetchGetExpensesDailyBreakdownQuery(variables: GetExpensesDailyBreakdownQueryVariables) {
  return { query: GetExpensesDailyBreakdownDocument, variables: variables };
}
export const GetOrganizationLimitHitsDocument = gql`
  query GetOrganizationLimitHits($organizationId: ID!, $constraintId: ID!) {
    organizationLimitHits(organizationId: $organizationId, constraintId: $constraintId) {
      run_result
      created_at
      value
      constraint_limit
    }
  }
`;

/**
 * __useGetOrganizationLimitHitsQuery__
 *
 * To run a query within a React component, call `useGetOrganizationLimitHitsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetOrganizationLimitHitsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetOrganizationLimitHitsQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      constraintId: // value for 'constraintId'
 *   },
 * });
 */
export function useGetOrganizationLimitHitsQuery(
  baseOptions: Apollo.QueryHookOptions<GetOrganizationLimitHitsQuery, GetOrganizationLimitHitsQueryVariables> &
    ({ variables: GetOrganizationLimitHitsQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetOrganizationLimitHitsQuery, GetOrganizationLimitHitsQueryVariables>(
    GetOrganizationLimitHitsDocument,
    options
  );
}
export function useGetOrganizationLimitHitsLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<GetOrganizationLimitHitsQuery, GetOrganizationLimitHitsQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetOrganizationLimitHitsQuery, GetOrganizationLimitHitsQueryVariables>(
    GetOrganizationLimitHitsDocument,
    options
  );
}
export function useGetOrganizationLimitHitsSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<GetOrganizationLimitHitsQuery, GetOrganizationLimitHitsQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<GetOrganizationLimitHitsQuery, GetOrganizationLimitHitsQueryVariables>(
    GetOrganizationLimitHitsDocument,
    options
  );
}
export type GetOrganizationLimitHitsQueryHookResult = ReturnType<typeof useGetOrganizationLimitHitsQuery>;
export type GetOrganizationLimitHitsLazyQueryHookResult = ReturnType<typeof useGetOrganizationLimitHitsLazyQuery>;
export type GetOrganizationLimitHitsSuspenseQueryHookResult = ReturnType<typeof useGetOrganizationLimitHitsSuspenseQuery>;
export type GetOrganizationLimitHitsQueryResult = Apollo.QueryResult<
  GetOrganizationLimitHitsQuery,
  GetOrganizationLimitHitsQueryVariables
>;
export function refetchGetOrganizationLimitHitsQuery(variables: GetOrganizationLimitHitsQueryVariables) {
  return { query: GetOrganizationLimitHitsDocument, variables: variables };
}
export const RelevantFlavorsDocument = gql`
  query RelevantFlavors($organizationId: ID!, $requestParams: JSONObject) {
    relevantFlavors(organizationId: $organizationId, requestParams: $requestParams)
  }
`;

/**
 * __useRelevantFlavorsQuery__
 *
 * To run a query within a React component, call `useRelevantFlavorsQuery` and pass it any options that fit your needs.
 * When your component renders, `useRelevantFlavorsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useRelevantFlavorsQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      requestParams: // value for 'requestParams'
 *   },
 * });
 */
export function useRelevantFlavorsQuery(
  baseOptions: Apollo.QueryHookOptions<RelevantFlavorsQuery, RelevantFlavorsQueryVariables> &
    ({ variables: RelevantFlavorsQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<RelevantFlavorsQuery, RelevantFlavorsQueryVariables>(RelevantFlavorsDocument, options);
}
export function useRelevantFlavorsLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<RelevantFlavorsQuery, RelevantFlavorsQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<RelevantFlavorsQuery, RelevantFlavorsQueryVariables>(RelevantFlavorsDocument, options);
}
export function useRelevantFlavorsSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<RelevantFlavorsQuery, RelevantFlavorsQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<RelevantFlavorsQuery, RelevantFlavorsQueryVariables>(RelevantFlavorsDocument, options);
}
export type RelevantFlavorsQueryHookResult = ReturnType<typeof useRelevantFlavorsQuery>;
export type RelevantFlavorsLazyQueryHookResult = ReturnType<typeof useRelevantFlavorsLazyQuery>;
export type RelevantFlavorsSuspenseQueryHookResult = ReturnType<typeof useRelevantFlavorsSuspenseQuery>;
export type RelevantFlavorsQueryResult = Apollo.QueryResult<RelevantFlavorsQuery, RelevantFlavorsQueryVariables>;
export function refetchRelevantFlavorsQuery(variables: RelevantFlavorsQueryVariables) {
  return { query: RelevantFlavorsDocument, variables: variables };
}
export const CleanExpensesDocument = gql`
  query CleanExpenses($organizationId: ID!, $params: CleanExpensesParams) {
    cleanExpenses(organizationId: $organizationId, params: $params)
  }
`;

/**
 * __useCleanExpensesQuery__
 *
 * To run a query within a React component, call `useCleanExpensesQuery` and pass it any options that fit your needs.
 * When your component renders, `useCleanExpensesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useCleanExpensesQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useCleanExpensesQuery(
  baseOptions: Apollo.QueryHookOptions<CleanExpensesQuery, CleanExpensesQueryVariables> &
    ({ variables: CleanExpensesQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<CleanExpensesQuery, CleanExpensesQueryVariables>(CleanExpensesDocument, options);
}
export function useCleanExpensesLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<CleanExpensesQuery, CleanExpensesQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<CleanExpensesQuery, CleanExpensesQueryVariables>(CleanExpensesDocument, options);
}
export function useCleanExpensesSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<CleanExpensesQuery, CleanExpensesQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<CleanExpensesQuery, CleanExpensesQueryVariables>(CleanExpensesDocument, options);
}
export type CleanExpensesQueryHookResult = ReturnType<typeof useCleanExpensesQuery>;
export type CleanExpensesLazyQueryHookResult = ReturnType<typeof useCleanExpensesLazyQuery>;
export type CleanExpensesSuspenseQueryHookResult = ReturnType<typeof useCleanExpensesSuspenseQuery>;
export type CleanExpensesQueryResult = Apollo.QueryResult<CleanExpensesQuery, CleanExpensesQueryVariables>;
export function refetchCleanExpensesQuery(variables: CleanExpensesQueryVariables) {
  return { query: CleanExpensesDocument, variables: variables };
}
export const CloudPoliciesDocument = gql`
  query CloudPolicies($organizationId: ID!, $params: CloudPoliciesParams) {
    cloudPolicies(organizationId: $organizationId, params: $params)
  }
`;

/**
 * __useCloudPoliciesQuery__
 *
 * To run a query within a React component, call `useCloudPoliciesQuery` and pass it any options that fit your needs.
 * When your component renders, `useCloudPoliciesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useCloudPoliciesQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useCloudPoliciesQuery(
  baseOptions: Apollo.QueryHookOptions<CloudPoliciesQuery, CloudPoliciesQueryVariables> &
    ({ variables: CloudPoliciesQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<CloudPoliciesQuery, CloudPoliciesQueryVariables>(CloudPoliciesDocument, options);
}
export function useCloudPoliciesLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<CloudPoliciesQuery, CloudPoliciesQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<CloudPoliciesQuery, CloudPoliciesQueryVariables>(CloudPoliciesDocument, options);
}
export function useCloudPoliciesSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<CloudPoliciesQuery, CloudPoliciesQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<CloudPoliciesQuery, CloudPoliciesQueryVariables>(CloudPoliciesDocument, options);
}
export type CloudPoliciesQueryHookResult = ReturnType<typeof useCloudPoliciesQuery>;
export type CloudPoliciesLazyQueryHookResult = ReturnType<typeof useCloudPoliciesLazyQuery>;
export type CloudPoliciesSuspenseQueryHookResult = ReturnType<typeof useCloudPoliciesSuspenseQuery>;
export type CloudPoliciesQueryResult = Apollo.QueryResult<CloudPoliciesQuery, CloudPoliciesQueryVariables>;
export function refetchCloudPoliciesQuery(variables: CloudPoliciesQueryVariables) {
  return { query: CloudPoliciesDocument, variables: variables };
}
export const AvailableFiltersDocument = gql`
  query AvailableFilters($organizationId: ID!, $params: AvailableFiltersParams) {
    availableFilters(organizationId: $organizationId, params: $params)
  }
`;

/**
 * __useAvailableFiltersQuery__
 *
 * To run a query within a React component, call `useAvailableFiltersQuery` and pass it any options that fit your needs.
 * When your component renders, `useAvailableFiltersQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAvailableFiltersQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useAvailableFiltersQuery(
  baseOptions: Apollo.QueryHookOptions<AvailableFiltersQuery, AvailableFiltersQueryVariables> &
    ({ variables: AvailableFiltersQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<AvailableFiltersQuery, AvailableFiltersQueryVariables>(AvailableFiltersDocument, options);
}
export function useAvailableFiltersLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<AvailableFiltersQuery, AvailableFiltersQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<AvailableFiltersQuery, AvailableFiltersQueryVariables>(AvailableFiltersDocument, options);
}
export function useAvailableFiltersSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<AvailableFiltersQuery, AvailableFiltersQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<AvailableFiltersQuery, AvailableFiltersQueryVariables>(AvailableFiltersDocument, options);
}
export type AvailableFiltersQueryHookResult = ReturnType<typeof useAvailableFiltersQuery>;
export type AvailableFiltersLazyQueryHookResult = ReturnType<typeof useAvailableFiltersLazyQuery>;
export type AvailableFiltersSuspenseQueryHookResult = ReturnType<typeof useAvailableFiltersSuspenseQuery>;
export type AvailableFiltersQueryResult = Apollo.QueryResult<AvailableFiltersQuery, AvailableFiltersQueryVariables>;
export function refetchAvailableFiltersQuery(variables: AvailableFiltersQueryVariables) {
  return { query: AvailableFiltersDocument, variables: variables };
}
