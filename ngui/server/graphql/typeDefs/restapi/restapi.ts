import { gql } from "graphql-tag";

export default gql`
  scalar JSONObject

  # use enum to get types for the "dataSource.type" field in revolver
  enum DataSourceType {
    aws_cnr
    azure_tenant
    azure_cnr
    gcp_cnr
    gcp_tenant
    alibaba_cnr
    nebius
    databricks
    kubernetes_cnr
    environment
  }

  type DataSourceDiscoveryInfos {
    cloud_account_id: String!
    created_at: Int!
    deleted_at: Int!
    enabled: Boolean
    id: String!
    last_discovery_at: Int!
    last_error: String
    last_error_at: Int!
    observe_time: Int!
    resource_type: String
  }

  type DataSourceDetails {
    cost: Float!
    discovery_infos: [DataSourceDiscoveryInfos]
    forecast: Float!
    last_month_cost: Float
    resources: Int!
  }

  interface DataSourceInterface {
    id: String
    created_at: Int
    name: String
    type: DataSourceType
    parent_id: String
    account_id: String
    last_import_at: Int
    last_import_attempt_at: Int
    last_import_attempt_error: String
    last_getting_metrics_at: Int
    last_getting_metric_attempt_at: Int
    last_getting_metric_attempt_error: String
    details: DataSourceDetails
  }

  # AWS data source
  type AwsConfig {
    access_key_id: String
    assume_role_account_id: String
    assume_role_name: String
    linked: Boolean
    use_edp_discount: Boolean
    cur_version: Int
    bucket_name: String
    bucket_prefix: String
    config_scheme: String
    region_name: String
    report_name: String
  }

  type AwsDataSource implements DataSourceInterface {
    id: String!
    created_at: Int
    name: String!
    type: DataSourceType!
    parent_id: String
    account_id: String!
    last_import_at: Int!
    last_import_attempt_at: Int!
    last_import_attempt_error: String
    last_getting_metrics_at: Int!
    last_getting_metric_attempt_at: Int!
    last_getting_metric_attempt_error: String
    details: DataSourceDetails
    config: AwsConfig
  }

  # Azure tenant data source
  type AzureTenantConfig {
    client_id: String
    tenant: String
  }

  type AzureTenantDataSource implements DataSourceInterface {
    id: String!
    created_at: Int
    name: String!
    type: DataSourceType!
    parent_id: String
    account_id: String!
    last_import_at: Int!
    last_import_attempt_at: Int!
    last_import_attempt_error: String
    last_getting_metrics_at: Int!
    last_getting_metric_attempt_at: Int!
    last_getting_metric_attempt_error: String
    details: DataSourceDetails
    config: AzureTenantConfig
  }

  # Azure subscription data source
  type AzureSubscriptionConfig {
    client_id: String
    expense_import_scheme: String
    subscription_id: String
    tenant: String
    export_name: String
    container: String
    directory: String
  }

  type AzureSubscriptionDataSource implements DataSourceInterface {
    id: String!
    created_at: Int
    name: String!
    type: DataSourceType!
    parent_id: String
    account_id: String!
    last_import_at: Int!
    last_import_attempt_at: Int!
    last_import_attempt_error: String
    last_getting_metrics_at: Int!
    last_getting_metric_attempt_at: Int!
    last_getting_metric_attempt_error: String
    details: DataSourceDetails
    config: AzureSubscriptionConfig
  }

  # GCP data source
  type GcpBillingDataConfig {
    dataset_name: String!
    table_name: String!
    project_id: String
  }

  type GcpPricingDataConfig {
    dataset_name: String!
    table_name: String!
    project_id: String
  }

  type GcpConfig {
    billing_data: GcpBillingDataConfig
    pricing_data: GcpPricingDataConfig
  }

  type GcpDataSource implements DataSourceInterface {
    id: String!
    created_at: Int
    name: String!
    type: DataSourceType!
    parent_id: String
    account_id: String!
    last_import_at: Int!
    last_import_attempt_at: Int!
    last_import_attempt_error: String
    last_getting_metrics_at: Int!
    last_getting_metric_attempt_at: Int!
    last_getting_metric_attempt_error: String
    details: DataSourceDetails
    config: GcpConfig
  }

  # GCP tenant data source
  type GcpTenantBillingDataConfig {
    dataset_name: String!
    table_name: String!
    project_id: String
  }

  type GcpTenantPricingDataConfig {
    dataset_name: String!
    table_name: String!
    project_id: String
  }

  type GcpTenantConfig {
    billing_data: GcpTenantBillingDataConfig
    pricing_data: GcpTenantPricingDataConfig
  }

  type GcpTenantDataSource implements DataSourceInterface {
    id: String!
    created_at: Int
    name: String!
    type: DataSourceType!
    parent_id: String
    account_id: String
    last_import_at: Int!
    last_import_attempt_at: Int!
    last_import_attempt_error: String
    last_getting_metrics_at: Int!
    last_getting_metric_attempt_at: Int!
    last_getting_metric_attempt_error: String
    details: DataSourceDetails
    config: GcpTenantConfig
  }

  # Alibaba data source
  type AlibabaConfig {
    access_key_id: String
  }

  type AlibabaDataSource implements DataSourceInterface {
    id: String!
    created_at: Int
    name: String!
    type: DataSourceType!
    parent_id: String
    account_id: String!
    last_import_at: Int!
    last_import_attempt_at: Int!
    last_import_attempt_error: String
    last_getting_metrics_at: Int!
    last_getting_metric_attempt_at: Int!
    last_getting_metric_attempt_error: String
    details: DataSourceDetails
    config: AlibabaConfig
  }

  # Nebius data source
  type NebiusConfig {
    cloud_name: String
    service_account_id: String
    key_id: String
    access_key_id: String
    # Make bucket name and prefix optional to fix conflicting types
    # to make it compatible with the AwsConfig type
    bucket_name: String
    bucket_prefix: String
  }

  type NebiusDataSource implements DataSourceInterface {
    id: String!
    created_at: Int
    name: String!
    type: DataSourceType!
    parent_id: String
    account_id: String!
    last_import_at: Int!
    last_import_attempt_at: Int!
    last_import_attempt_error: String
    last_getting_metrics_at: Int!
    last_getting_metric_attempt_at: Int!
    last_getting_metric_attempt_error: String
    details: DataSourceDetails
    config: NebiusConfig
  }

  # Databricks data source
  type DatabricksConfig {
    account_id: String
    client_id: String
  }

  type DatabricksDataSource implements DataSourceInterface {
    id: String!
    created_at: Int
    name: String!
    type: DataSourceType!
    parent_id: String
    account_id: String!
    last_import_at: Int!
    last_import_attempt_at: Int!
    last_import_attempt_error: String
    last_getting_metrics_at: Int!
    last_getting_metric_attempt_at: Int!
    last_getting_metric_attempt_error: String
    details: DataSourceDetails
    config: DatabricksConfig
  }

  # K8s data source
  type K8CostModelConfig {
    cpu_hourly_cost: Float!
    memory_hourly_cost: Float!
  }

  type K8sConfig {
    cost_model: K8CostModelConfig
    user: String
    custom_price: Boolean
  }

  type K8sDataSource implements DataSourceInterface {
    id: String!
    created_at: Int
    name: String!
    type: DataSourceType!
    parent_id: String
    account_id: String!
    last_import_at: Int!
    last_import_attempt_at: Int!
    last_import_attempt_error: String
    last_getting_metrics_at: Int!
    last_getting_metric_attempt_at: Int!
    last_getting_metric_attempt_error: String
    details: DataSourceDetails
    config: K8sConfig
  }

  # Environment data source
  type EnvironmentDataSource implements DataSourceInterface {
    id: String!
    created_at: Int
    name: String!
    type: DataSourceType!
    parent_id: String
    account_id: String!
    last_import_at: Int!
    last_import_attempt_at: Int!
    last_import_attempt_error: String
    last_getting_metrics_at: Int!
    last_getting_metric_attempt_at: Int!
    last_getting_metric_attempt_error: String
    details: DataSourceDetails
  }

  input DataSourceRequestParams {
    details: Boolean
  }

  input AwsRootConfigInput {
    access_key_id: String!
    secret_access_key: String!
    use_edp_discount: Boolean
    cur_version: Int
    bucket_name: String
    bucket_prefix: String
    config_scheme: String
    report_name: String
    region_name: String
  }

  input AwsLinkedConfigInput {
    access_key_id: String!
    secret_access_key: String!
    linked: Boolean!
  }

  input AwsAssumedRoleConfigInput {
    assume_role_account_id: String!
    assume_role_name: String!
    bucket_name: String
    bucket_prefix: String
    region_name: String
    use_edp_discount: Boolean
    cur_version: Int
    config_scheme: String
    report_name: String
  }

  input AzureSubscriptionConfigInput {
    client_id: String!
    secret: String!
    subscription_id: String!
    tenant: String!
    export_name: String
    sa_connection_string: String
    container: String
    directory: String
  }

  input AzureTenantConfigInput {
    client_id: String!
    secret: String!
    tenant: String!
  }

  input GcpBillingDataConfigInput {
    dataset_name: String!
    table_name: String!
    project_id: String
  }

  input GcpPricingDataConfigInput {
    dataset_name: String!
    table_name: String!
    project_id: String
  }

  input GcpConfigInput {
    billing_data: GcpBillingDataConfigInput!
    pricing_data: GcpPricingDataConfigInput
    credentials: JSONObject!
  }

  input GcpTenantConfigInput {
    billing_data: GcpBillingDataConfigInput!
    pricing_data: GcpPricingDataConfigInput
    credentials: JSONObject!
  }

  input AlibabaConfigInput {
    access_key_id: String!
    secret_access_key: String!
  }

  input NebiusConfigInput {
    cloud_name: String!
    service_account_id: String!
    key_id: String!
    private_key: String!
    access_key_id: String!
    secret_access_key: String!
    bucket_name: String!
    bucket_prefix: String
  }

  input K8sConfigInput {
    password: String!
    user: String!
    cost_model: JSONObject
    custom_price: Boolean
  }

  input DatabricksConfigInput {
    account_id: String!
    client_id: String!
    client_secret: String!
  }

  input CreateDataSourceInput {
    name: String
    type: String
    awsRootConfig: AwsRootConfigInput
    awsLinkedConfig: AwsLinkedConfigInput
    awsAssumedRoleConfig: AwsAssumedRoleConfigInput
    azureSubscriptionConfig: AzureSubscriptionConfigInput
    azureTenantConfig: AzureTenantConfigInput
    gcpConfig: GcpConfigInput
    gcpTenantConfig: GcpTenantConfigInput
    alibabaConfig: AlibabaConfigInput
    nebiusConfig: NebiusConfigInput
    databricksConfig: DatabricksConfigInput
    k8sConfig: K8sConfigInput
  }

  input UpdateDataSourceInput {
    name: String
    lastImportAt: Int
    lastImportModifiedAt: Int
    awsRootConfig: AwsRootConfigInput
    awsLinkedConfig: AwsLinkedConfigInput
    awsAssumedRoleConfig: AwsAssumedRoleConfigInput
    azureSubscriptionConfig: AzureSubscriptionConfigInput
    azureTenantConfig: AzureTenantConfigInput
    gcpConfig: GcpConfigInput
    gcpTenantConfig: GcpTenantConfigInput
    alibabaConfig: AlibabaConfigInput
    nebiusConfig: NebiusConfigInput
    databricksConfig: DatabricksConfigInput
    k8sConfig: K8sConfigInput
  }

  type EmployeeEmail {
    id: ID!
    employee_id: ID!
    email_template: String!
    enabled: Boolean!
    available_by_role: Boolean!
  }

  input UpdateEmployeeEmailsInput {
    enable: [ID!]
    disable: [ID!]
  }

  enum UpdateEmployeeEmailsAction {
    enable
    disable
  }

  input UpdateEmployeeEmailInput {
    emailId: ID!
    action: UpdateEmployeeEmailsAction!
  }
  enum OrganizationConstraintType {
    resource_count_anomaly
    expense_anomaly
    resource_quota
    recurring_budget
    expiring_budget
    tagging_policy
  }

  type OrganizationConstraint {
    created_at: Int!
    definition: JSONObject!
    deleted_at: Int!
    filters: JSONObject!
    id: ID!
    last_run: Int!
    last_run_result: JSONObject!
    name: String!
    organization_id: String!
    type: OrganizationConstraintType!
  }

  enum BreakdownBy {
    service_name
    region
    resource_type
    cloud_account_id
    employee_id
    pool_id
    k8s_node
    k8s_namespace
    k8s_service
  }

  input BreakdownParams {
    start_date: Int!
    end_date: Int!
    breakdown_by: String!
    cloud_account_id: [String!]
    pool_id: [String!]
    owner_id: [String!]
    region: [String!]
    service_name: [String!]
    resource_type: [String!]
    active: [Boolean!]
    recommendations: [Boolean!]
    constraint_violated: [Boolean!]
    first_seen_gte: Int
    first_seen_lte: Int
    last_seen_gte: Int
    last_seen_lte: Int
    tag: [String!]
    without_tag: [String!]
    meta: [String!]
    traffic_from: [String!]
    traffic_to: [String!]
    k8s_node: [String!]
    k8s_service: [String!]
    k8s_namespace: [String!]
  }

  type ResourceCountBreakdown {
    start_date: Int!
    end_date: Int!
    count: Int!
    breakdown: JSONObject!
    first_breakdown: Int!
    last_breakdown: Int!
    breakdown_by: BreakdownBy!
    counts: JSONObject!
  }

  type ExpensesDailyBreakdown {
    breakdown: JSONObject!
    breakdown_by: BreakdownBy!
    counts: JSONObject!
    previous_range_start: Int!
    previous_total: Int!
    start_date: Int!
    total: Int!
  }

  type MetaBreakdown {
    breakdown: JSONObject!
    totals: JSONObject!
    start_date: Int!
    end_date: Int!
  }

  type OrganizationLimitHit {
    constraint_id: String!
    constraint_limit: Float!
    created_at: Int!
    deleted_at: Int!
    value: Float!
    id: ID!
    organization_id: String!
    run_result: JSONObject!
  }

  type Organization {
    id: String!
    name: String!
    is_demo: Boolean!
    currency: String!
    pool_id: String!
    disabled: Boolean!
  }

  type Employee {
    id: String!
    jira_connected: Boolean!
    slack_connected: Boolean!
  }

  type InvitationAssignment {
    id: String!
    scope_id: String!
    scope_name: String!
    scope_type: String!
    purpose: String!
  }

  type Invitation {
    id: String!
    owner_name: String!
    owner_email: String!
    organization: String!
    invite_assignments: [InvitationAssignment!]
  }

  input UpdateOrganizationInput {
    name: String
    currency: String
  }

  input CleanExpensesParams {
    start_date: Int!
    end_date: Int!
    limit: Int
    active: [Boolean]
    constraint_violated: [Boolean]
    recommendations: [Boolean]
    cloud_account_id: [String]
    format: [String]
    k8s_namespace: [String]
    k8s_node: [String]
    k8s_service: [String]
    owner_id: [String]
    pool_id: [String]
    region: [String]
    resource_type: [String]
    service_name: [String]
    tag: [String]
    without_tag: [String]
    meta: [String]
    traffic_from: [String]
    traffic_to: [String]
    first_seen_gte: Int
    first_seen_lte: Int
    last_seen_gte: Int
    last_seen_lte: Int
  }

  input CloudPoliciesParams {
    bucket_name: String!
    cloud_type: String!
  }

  input AvailableFiltersParams {
    start_date: Int!
    end_date: Int!
    cloud_account_id: [String!]
    pool_id: [String!]
    owner_id: [String!]
    region: [String!]
    service_name: [String!]
    resource_type: [String!]
    active: [Boolean!]
    recommendations: [Boolean!]
    constraint_violated: [Boolean!]
    first_seen_gte: Int
    first_seen_lte: Int
    last_seen_gte: Int
    last_seen_lte: Int
    tag: [String!]
    without_tag: [String!]
    meta: [String!]
    traffic_from: [String!]
    traffic_to: [String!]
    k8s_node: [String!]
    k8s_service: [String!]
    k8s_namespace: [String!]
  }

  type Query {
    organizations: [Organization!]!
    currentEmployee(organizationId: ID!): Employee
    dataSources(organizationId: ID!): [DataSourceInterface]
    dataSource(dataSourceId: ID!, requestParams: DataSourceRequestParams): DataSourceInterface
    employeeEmails(employeeId: ID!): [EmployeeEmail]
    invitations: [Invitation]
    organizationFeatures(organizationId: ID!): JSONObject
    organizationThemeSettings(organizationId: ID!): JSONObject
    organizationPerspectives(organizationId: ID!): JSONObject
    organizationConstraint(constraintId: ID!): OrganizationConstraint
    resourceCountBreakdown(organizationId: ID!, params: BreakdownParams): ResourceCountBreakdown
    expensesDailyBreakdown(organizationId: ID!, params: BreakdownParams): ExpensesDailyBreakdown
    metaBreakdown(organizationId: ID!, params: BreakdownParams): MetaBreakdown
    organizationLimitHits(organizationId: ID!, constraintId: ID!): [OrganizationLimitHit!]
    relevantFlavors(organizationId: ID!, requestParams: JSONObject): JSONObject
    cleanExpenses(organizationId: ID!, params: CleanExpensesParams): JSONObject
    cloudPolicies(organizationId: ID!, params: CloudPoliciesParams): JSONObject
    availableFilters(organizationId: ID!, params: AvailableFiltersParams): JSONObject
  }

  type Mutation {
    createDataSource(organizationId: ID!, params: CreateDataSourceInput!): DataSourceInterface
    updateDataSource(dataSourceId: ID!, params: UpdateDataSourceInput!): DataSourceInterface
    updateEmployeeEmails(employeeId: ID!, params: UpdateEmployeeEmailsInput!): [EmployeeEmail]
    updateEmployeeEmail(employeeId: ID!, params: UpdateEmployeeEmailInput!): EmployeeEmail
    deleteDataSource(dataSourceId: ID!): String
    createOrganization(organizationName: String!): Organization
    updateOrganization(organizationId: ID!, params: UpdateOrganizationInput!): Organization
    deleteOrganization(organizationId: ID!): String
    updateInvitation(invitationId: String!, action: String!): String
    updateOrganizationThemeSettings(organizationId: ID!, value: JSONObject!): JSONObject
    updateOrganizationPerspectives(organizationId: ID!, value: JSONObject!): JSONObject
  }
`;
