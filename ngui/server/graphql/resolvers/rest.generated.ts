import { GraphQLResolveInfo } from 'graphql';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
export type RequireFields<T, K extends keyof T> = Omit<T, K> & { [P in K]-?: NonNullable<T[P]> };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
};

export type AlibabaConfig = {
  __typename?: 'AlibabaConfig';
  access_key_id: Scalars['String']['output'];
};

export type AlibabaDataSource = DataSourceInterface & {
  __typename?: 'AlibabaDataSource';
  account_id: Scalars['String']['output'];
  config?: Maybe<AlibabaConfig>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars['String']['output'];
  last_getting_metric_attempt_at: Scalars['Int']['output'];
  last_getting_metric_attempt_error?: Maybe<Scalars['String']['output']>;
  last_getting_metrics_at: Scalars['Int']['output'];
  last_import_at: Scalars['Int']['output'];
  last_import_attempt_at: Scalars['Int']['output'];
  last_import_attempt_error?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parent_id?: Maybe<Scalars['String']['output']>;
  type: DataSourceType;
};

export type AwsConfig = {
  __typename?: 'AwsConfig';
  access_key_id: Scalars['String']['output'];
  bucket_name?: Maybe<Scalars['String']['output']>;
  bucket_prefix?: Maybe<Scalars['String']['output']>;
  config_scheme?: Maybe<Scalars['String']['output']>;
  linked: Scalars['Boolean']['output'];
  region_name?: Maybe<Scalars['String']['output']>;
  report_name?: Maybe<Scalars['String']['output']>;
};

export type AwsDataSource = DataSourceInterface & {
  __typename?: 'AwsDataSource';
  account_id: Scalars['String']['output'];
  config?: Maybe<AwsConfig>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars['String']['output'];
  last_getting_metric_attempt_at: Scalars['Int']['output'];
  last_getting_metric_attempt_error?: Maybe<Scalars['String']['output']>;
  last_getting_metrics_at: Scalars['Int']['output'];
  last_import_at: Scalars['Int']['output'];
  last_import_attempt_at: Scalars['Int']['output'];
  last_import_attempt_error?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parent_id?: Maybe<Scalars['String']['output']>;
  type: DataSourceType;
};

export type AzureSubscriptionConfig = {
  __typename?: 'AzureSubscriptionConfig';
  client_id: Scalars['String']['output'];
  expense_import_scheme: Scalars['String']['output'];
  subscription_id: Scalars['String']['output'];
  tenant: Scalars['String']['output'];
};

export type AzureSubscriptionDataSource = DataSourceInterface & {
  __typename?: 'AzureSubscriptionDataSource';
  account_id: Scalars['String']['output'];
  config?: Maybe<AzureSubscriptionConfig>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars['String']['output'];
  last_getting_metric_attempt_at: Scalars['Int']['output'];
  last_getting_metric_attempt_error?: Maybe<Scalars['String']['output']>;
  last_getting_metrics_at: Scalars['Int']['output'];
  last_import_at: Scalars['Int']['output'];
  last_import_attempt_at: Scalars['Int']['output'];
  last_import_attempt_error?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parent_id?: Maybe<Scalars['String']['output']>;
  type: DataSourceType;
};

export type AzureTenantConfig = {
  __typename?: 'AzureTenantConfig';
  client_id: Scalars['String']['output'];
  tenant: Scalars['String']['output'];
};

export type AzureTenantDataSource = DataSourceInterface & {
  __typename?: 'AzureTenantDataSource';
  account_id: Scalars['String']['output'];
  config?: Maybe<AzureTenantConfig>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars['String']['output'];
  last_getting_metric_attempt_at: Scalars['Int']['output'];
  last_getting_metric_attempt_error?: Maybe<Scalars['String']['output']>;
  last_getting_metrics_at: Scalars['Int']['output'];
  last_import_at: Scalars['Int']['output'];
  last_import_attempt_at: Scalars['Int']['output'];
  last_import_attempt_error?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parent_id?: Maybe<Scalars['String']['output']>;
  type: DataSourceType;
};

export type DataSourceDetails = {
  __typename?: 'DataSourceDetails';
  cost: Scalars['Float']['output'];
  discovery_infos?: Maybe<Array<Maybe<DataSourceDiscoveryInfos>>>;
  forecast: Scalars['Float']['output'];
  last_month_cost: Scalars['Float']['output'];
  resources: Scalars['Int']['output'];
};

export type DataSourceDiscoveryInfos = {
  __typename?: 'DataSourceDiscoveryInfos';
  cloud_account_id: Scalars['String']['output'];
  created_at: Scalars['Int']['output'];
  deleted_at: Scalars['Int']['output'];
  enabled?: Maybe<Scalars['Boolean']['output']>;
  id: Scalars['String']['output'];
  last_discovery_at: Scalars['Int']['output'];
  last_error?: Maybe<Scalars['String']['output']>;
  last_error_at: Scalars['Int']['output'];
  observe_time: Scalars['Int']['output'];
  resource_type?: Maybe<Scalars['String']['output']>;
};

export type DataSourceInterface = {
  account_id: Scalars['String']['output'];
  details?: Maybe<DataSourceDetails>;
  id: Scalars['String']['output'];
  last_getting_metric_attempt_at: Scalars['Int']['output'];
  last_getting_metric_attempt_error?: Maybe<Scalars['String']['output']>;
  last_getting_metrics_at: Scalars['Int']['output'];
  last_import_at: Scalars['Int']['output'];
  last_import_attempt_at: Scalars['Int']['output'];
  last_import_attempt_error?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parent_id?: Maybe<Scalars['String']['output']>;
  type: DataSourceType;
};

export type DataSourceRequestParams = {
  details?: InputMaybe<Scalars['Boolean']['input']>;
};

export enum DataSourceType {
  AlibabaCnr = 'alibaba_cnr',
  AwsCnr = 'aws_cnr',
  AzureCnr = 'azure_cnr',
  AzureTenant = 'azure_tenant',
  Databricks = 'databricks',
  Environment = 'environment',
  GcpCnr = 'gcp_cnr',
  KubernetesCnr = 'kubernetes_cnr',
  Nebius = 'nebius'
}

export type DatabricksConfig = {
  __typename?: 'DatabricksConfig';
  account_id: Scalars['String']['output'];
  client_id: Scalars['String']['output'];
};

export type DatabricksDataSource = DataSourceInterface & {
  __typename?: 'DatabricksDataSource';
  account_id: Scalars['String']['output'];
  config?: Maybe<DatabricksConfig>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars['String']['output'];
  last_getting_metric_attempt_at: Scalars['Int']['output'];
  last_getting_metric_attempt_error?: Maybe<Scalars['String']['output']>;
  last_getting_metrics_at: Scalars['Int']['output'];
  last_import_at: Scalars['Int']['output'];
  last_import_attempt_at: Scalars['Int']['output'];
  last_import_attempt_error?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parent_id?: Maybe<Scalars['String']['output']>;
  type: DataSourceType;
};

export type EnvironmentDataSource = DataSourceInterface & {
  __typename?: 'EnvironmentDataSource';
  account_id: Scalars['String']['output'];
  details?: Maybe<DataSourceDetails>;
  id: Scalars['String']['output'];
  last_getting_metric_attempt_at: Scalars['Int']['output'];
  last_getting_metric_attempt_error?: Maybe<Scalars['String']['output']>;
  last_getting_metrics_at: Scalars['Int']['output'];
  last_import_at: Scalars['Int']['output'];
  last_import_attempt_at: Scalars['Int']['output'];
  last_import_attempt_error?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parent_id?: Maybe<Scalars['String']['output']>;
  type: DataSourceType;
};

export type GcpBillingDataConfig = {
  __typename?: 'GcpBillingDataConfig';
  dataset_name: Scalars['String']['output'];
  table_name: Scalars['String']['output'];
};

export type GcpConfig = {
  __typename?: 'GcpConfig';
  billing_data: GcpBillingDataConfig;
};

export type GcpDataSource = DataSourceInterface & {
  __typename?: 'GcpDataSource';
  account_id: Scalars['String']['output'];
  config?: Maybe<GcpConfig>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars['String']['output'];
  last_getting_metric_attempt_at: Scalars['Int']['output'];
  last_getting_metric_attempt_error?: Maybe<Scalars['String']['output']>;
  last_getting_metrics_at: Scalars['Int']['output'];
  last_import_at: Scalars['Int']['output'];
  last_import_attempt_at: Scalars['Int']['output'];
  last_import_attempt_error?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parent_id?: Maybe<Scalars['String']['output']>;
  type: DataSourceType;
};

export type K8CostModelConfig = {
  __typename?: 'K8CostModelConfig';
  cpu_hourly_cost: Scalars['Float']['output'];
  memory_hourly_cost: Scalars['Float']['output'];
};

export type K8sConfig = {
  __typename?: 'K8sConfig';
  cost_model?: Maybe<K8CostModelConfig>;
  user: Scalars['String']['output'];
};

export type K8sDataSource = DataSourceInterface & {
  __typename?: 'K8sDataSource';
  account_id: Scalars['String']['output'];
  config?: Maybe<K8sConfig>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars['String']['output'];
  last_getting_metric_attempt_at: Scalars['Int']['output'];
  last_getting_metric_attempt_error?: Maybe<Scalars['String']['output']>;
  last_getting_metrics_at: Scalars['Int']['output'];
  last_import_at: Scalars['Int']['output'];
  last_import_attempt_at: Scalars['Int']['output'];
  last_import_attempt_error?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parent_id?: Maybe<Scalars['String']['output']>;
  type: DataSourceType;
};

export type NebiusConfig = {
  __typename?: 'NebiusConfig';
  access_key_id: Scalars['String']['output'];
  bucket_name?: Maybe<Scalars['String']['output']>;
  bucket_prefix?: Maybe<Scalars['String']['output']>;
  cloud_name: Scalars['String']['output'];
  key_id: Scalars['String']['output'];
  service_account_id: Scalars['String']['output'];
};

export type NebiusDataSource = DataSourceInterface & {
  __typename?: 'NebiusDataSource';
  account_id: Scalars['String']['output'];
  config?: Maybe<NebiusConfig>;
  details?: Maybe<DataSourceDetails>;
  id: Scalars['String']['output'];
  last_getting_metric_attempt_at: Scalars['Int']['output'];
  last_getting_metric_attempt_error?: Maybe<Scalars['String']['output']>;
  last_getting_metrics_at: Scalars['Int']['output'];
  last_import_at: Scalars['Int']['output'];
  last_import_attempt_at: Scalars['Int']['output'];
  last_import_attempt_error?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parent_id?: Maybe<Scalars['String']['output']>;
  type: DataSourceType;
};

export type Query = {
  __typename?: 'Query';
  dataSource?: Maybe<DataSourceInterface>;
};


export type QueryDataSourceArgs = {
  dataSourceId: Scalars['ID']['input'];
  requestParams?: InputMaybe<DataSourceRequestParams>;
};



export type ResolverTypeWrapper<T> = Promise<T> | T;


export type ResolverWithResolve<TResult, TParent, TContext, TArgs> = {
  resolve: ResolverFn<TResult, TParent, TContext, TArgs>;
};
export type Resolver<TResult, TParent = {}, TContext = {}, TArgs = {}> = ResolverFn<TResult, TParent, TContext, TArgs> | ResolverWithResolve<TResult, TParent, TContext, TArgs>;

export type ResolverFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => Promise<TResult> | TResult;

export type SubscriptionSubscribeFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => AsyncIterable<TResult> | Promise<AsyncIterable<TResult>>;

export type SubscriptionResolveFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => TResult | Promise<TResult>;

export interface SubscriptionSubscriberObject<TResult, TKey extends string, TParent, TContext, TArgs> {
  subscribe: SubscriptionSubscribeFn<{ [key in TKey]: TResult }, TParent, TContext, TArgs>;
  resolve?: SubscriptionResolveFn<TResult, { [key in TKey]: TResult }, TContext, TArgs>;
}

export interface SubscriptionResolverObject<TResult, TParent, TContext, TArgs> {
  subscribe: SubscriptionSubscribeFn<any, TParent, TContext, TArgs>;
  resolve: SubscriptionResolveFn<TResult, any, TContext, TArgs>;
}

export type SubscriptionObject<TResult, TKey extends string, TParent, TContext, TArgs> =
  | SubscriptionSubscriberObject<TResult, TKey, TParent, TContext, TArgs>
  | SubscriptionResolverObject<TResult, TParent, TContext, TArgs>;

export type SubscriptionResolver<TResult, TKey extends string, TParent = {}, TContext = {}, TArgs = {}> =
  | ((...args: any[]) => SubscriptionObject<TResult, TKey, TParent, TContext, TArgs>)
  | SubscriptionObject<TResult, TKey, TParent, TContext, TArgs>;

export type TypeResolveFn<TTypes, TParent = {}, TContext = {}> = (
  parent: TParent,
  context: TContext,
  info: GraphQLResolveInfo
) => Maybe<TTypes> | Promise<Maybe<TTypes>>;

export type IsTypeOfResolverFn<T = {}, TContext = {}> = (obj: T, context: TContext, info: GraphQLResolveInfo) => boolean | Promise<boolean>;

export type NextResolverFn<T> = () => Promise<T>;

export type DirectiveResolverFn<TResult = {}, TParent = {}, TContext = {}, TArgs = {}> = (
  next: NextResolverFn<TResult>,
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => TResult | Promise<TResult>;


/** Mapping of interface types */
export type ResolversInterfaceTypes<RefType extends Record<string, unknown>> = {
  DataSourceInterface: ( AlibabaDataSource ) | ( AwsDataSource ) | ( AzureSubscriptionDataSource ) | ( AzureTenantDataSource ) | ( DatabricksDataSource ) | ( EnvironmentDataSource ) | ( GcpDataSource ) | ( K8sDataSource ) | ( NebiusDataSource );
};

/** Mapping between all available schema types and the resolvers types */
export type ResolversTypes = {
  AlibabaConfig: ResolverTypeWrapper<AlibabaConfig>;
  AlibabaDataSource: ResolverTypeWrapper<AlibabaDataSource>;
  AwsConfig: ResolverTypeWrapper<AwsConfig>;
  AwsDataSource: ResolverTypeWrapper<AwsDataSource>;
  AzureSubscriptionConfig: ResolverTypeWrapper<AzureSubscriptionConfig>;
  AzureSubscriptionDataSource: ResolverTypeWrapper<AzureSubscriptionDataSource>;
  AzureTenantConfig: ResolverTypeWrapper<AzureTenantConfig>;
  AzureTenantDataSource: ResolverTypeWrapper<AzureTenantDataSource>;
  Boolean: ResolverTypeWrapper<Scalars['Boolean']['output']>;
  DataSourceDetails: ResolverTypeWrapper<DataSourceDetails>;
  DataSourceDiscoveryInfos: ResolverTypeWrapper<DataSourceDiscoveryInfos>;
  DataSourceInterface: ResolverTypeWrapper<ResolversInterfaceTypes<ResolversTypes>['DataSourceInterface']>;
  DataSourceRequestParams: DataSourceRequestParams;
  DataSourceType: DataSourceType;
  DatabricksConfig: ResolverTypeWrapper<DatabricksConfig>;
  DatabricksDataSource: ResolverTypeWrapper<DatabricksDataSource>;
  EnvironmentDataSource: ResolverTypeWrapper<EnvironmentDataSource>;
  Float: ResolverTypeWrapper<Scalars['Float']['output']>;
  GcpBillingDataConfig: ResolverTypeWrapper<GcpBillingDataConfig>;
  GcpConfig: ResolverTypeWrapper<GcpConfig>;
  GcpDataSource: ResolverTypeWrapper<GcpDataSource>;
  ID: ResolverTypeWrapper<Scalars['ID']['output']>;
  Int: ResolverTypeWrapper<Scalars['Int']['output']>;
  K8CostModelConfig: ResolverTypeWrapper<K8CostModelConfig>;
  K8sConfig: ResolverTypeWrapper<K8sConfig>;
  K8sDataSource: ResolverTypeWrapper<K8sDataSource>;
  NebiusConfig: ResolverTypeWrapper<NebiusConfig>;
  NebiusDataSource: ResolverTypeWrapper<NebiusDataSource>;
  Query: ResolverTypeWrapper<{}>;
  String: ResolverTypeWrapper<Scalars['String']['output']>;
};

/** Mapping between all available schema types and the resolvers parents */
export type ResolversParentTypes = {
  AlibabaConfig: AlibabaConfig;
  AlibabaDataSource: AlibabaDataSource;
  AwsConfig: AwsConfig;
  AwsDataSource: AwsDataSource;
  AzureSubscriptionConfig: AzureSubscriptionConfig;
  AzureSubscriptionDataSource: AzureSubscriptionDataSource;
  AzureTenantConfig: AzureTenantConfig;
  AzureTenantDataSource: AzureTenantDataSource;
  Boolean: Scalars['Boolean']['output'];
  DataSourceDetails: DataSourceDetails;
  DataSourceDiscoveryInfos: DataSourceDiscoveryInfos;
  DataSourceInterface: ResolversInterfaceTypes<ResolversParentTypes>['DataSourceInterface'];
  DataSourceRequestParams: DataSourceRequestParams;
  DatabricksConfig: DatabricksConfig;
  DatabricksDataSource: DatabricksDataSource;
  EnvironmentDataSource: EnvironmentDataSource;
  Float: Scalars['Float']['output'];
  GcpBillingDataConfig: GcpBillingDataConfig;
  GcpConfig: GcpConfig;
  GcpDataSource: GcpDataSource;
  ID: Scalars['ID']['output'];
  Int: Scalars['Int']['output'];
  K8CostModelConfig: K8CostModelConfig;
  K8sConfig: K8sConfig;
  K8sDataSource: K8sDataSource;
  NebiusConfig: NebiusConfig;
  NebiusDataSource: NebiusDataSource;
  Query: {};
  String: Scalars['String']['output'];
};

export type AlibabaConfigResolvers<ContextType = any, ParentType extends ResolversParentTypes['AlibabaConfig'] = ResolversParentTypes['AlibabaConfig']> = {
  access_key_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type AlibabaDataSourceResolvers<ContextType = any, ParentType extends ResolversParentTypes['AlibabaDataSource'] = ResolversParentTypes['AlibabaDataSource']> = {
  account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  config?: Resolver<Maybe<ResolversTypes['AlibabaConfig']>, ParentType, ContextType>;
  details?: Resolver<Maybe<ResolversTypes['DataSourceDetails']>, ParentType, ContextType>;
  id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  last_getting_metric_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_getting_metric_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  last_getting_metrics_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  parent_id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  type?: Resolver<ResolversTypes['DataSourceType'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type AwsConfigResolvers<ContextType = any, ParentType extends ResolversParentTypes['AwsConfig'] = ResolversParentTypes['AwsConfig']> = {
  access_key_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  bucket_name?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  bucket_prefix?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  config_scheme?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  linked?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>;
  region_name?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  report_name?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type AwsDataSourceResolvers<ContextType = any, ParentType extends ResolversParentTypes['AwsDataSource'] = ResolversParentTypes['AwsDataSource']> = {
  account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  config?: Resolver<Maybe<ResolversTypes['AwsConfig']>, ParentType, ContextType>;
  details?: Resolver<Maybe<ResolversTypes['DataSourceDetails']>, ParentType, ContextType>;
  id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  last_getting_metric_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_getting_metric_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  last_getting_metrics_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  parent_id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  type?: Resolver<ResolversTypes['DataSourceType'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type AzureSubscriptionConfigResolvers<ContextType = any, ParentType extends ResolversParentTypes['AzureSubscriptionConfig'] = ResolversParentTypes['AzureSubscriptionConfig']> = {
  client_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  expense_import_scheme?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  subscription_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  tenant?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type AzureSubscriptionDataSourceResolvers<ContextType = any, ParentType extends ResolversParentTypes['AzureSubscriptionDataSource'] = ResolversParentTypes['AzureSubscriptionDataSource']> = {
  account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  config?: Resolver<Maybe<ResolversTypes['AzureSubscriptionConfig']>, ParentType, ContextType>;
  details?: Resolver<Maybe<ResolversTypes['DataSourceDetails']>, ParentType, ContextType>;
  id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  last_getting_metric_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_getting_metric_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  last_getting_metrics_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  parent_id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  type?: Resolver<ResolversTypes['DataSourceType'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type AzureTenantConfigResolvers<ContextType = any, ParentType extends ResolversParentTypes['AzureTenantConfig'] = ResolversParentTypes['AzureTenantConfig']> = {
  client_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  tenant?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type AzureTenantDataSourceResolvers<ContextType = any, ParentType extends ResolversParentTypes['AzureTenantDataSource'] = ResolversParentTypes['AzureTenantDataSource']> = {
  account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  config?: Resolver<Maybe<ResolversTypes['AzureTenantConfig']>, ParentType, ContextType>;
  details?: Resolver<Maybe<ResolversTypes['DataSourceDetails']>, ParentType, ContextType>;
  id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  last_getting_metric_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_getting_metric_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  last_getting_metrics_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  parent_id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  type?: Resolver<ResolversTypes['DataSourceType'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type DataSourceDetailsResolvers<ContextType = any, ParentType extends ResolversParentTypes['DataSourceDetails'] = ResolversParentTypes['DataSourceDetails']> = {
  cost?: Resolver<ResolversTypes['Float'], ParentType, ContextType>;
  discovery_infos?: Resolver<Maybe<Array<Maybe<ResolversTypes['DataSourceDiscoveryInfos']>>>, ParentType, ContextType>;
  forecast?: Resolver<ResolversTypes['Float'], ParentType, ContextType>;
  last_month_cost?: Resolver<ResolversTypes['Float'], ParentType, ContextType>;
  resources?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type DataSourceDiscoveryInfosResolvers<ContextType = any, ParentType extends ResolversParentTypes['DataSourceDiscoveryInfos'] = ResolversParentTypes['DataSourceDiscoveryInfos']> = {
  cloud_account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  created_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  deleted_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  enabled?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>;
  id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  last_discovery_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  last_error_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  observe_time?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  resource_type?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type DataSourceInterfaceResolvers<ContextType = any, ParentType extends ResolversParentTypes['DataSourceInterface'] = ResolversParentTypes['DataSourceInterface']> = {
  __resolveType: TypeResolveFn<'AlibabaDataSource' | 'AwsDataSource' | 'AzureSubscriptionDataSource' | 'AzureTenantDataSource' | 'DatabricksDataSource' | 'EnvironmentDataSource' | 'GcpDataSource' | 'K8sDataSource' | 'NebiusDataSource', ParentType, ContextType>;
  account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  details?: Resolver<Maybe<ResolversTypes['DataSourceDetails']>, ParentType, ContextType>;
  id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  last_getting_metric_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_getting_metric_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  last_getting_metrics_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  parent_id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  type?: Resolver<ResolversTypes['DataSourceType'], ParentType, ContextType>;
};

export type DatabricksConfigResolvers<ContextType = any, ParentType extends ResolversParentTypes['DatabricksConfig'] = ResolversParentTypes['DatabricksConfig']> = {
  account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  client_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type DatabricksDataSourceResolvers<ContextType = any, ParentType extends ResolversParentTypes['DatabricksDataSource'] = ResolversParentTypes['DatabricksDataSource']> = {
  account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  config?: Resolver<Maybe<ResolversTypes['DatabricksConfig']>, ParentType, ContextType>;
  details?: Resolver<Maybe<ResolversTypes['DataSourceDetails']>, ParentType, ContextType>;
  id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  last_getting_metric_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_getting_metric_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  last_getting_metrics_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  parent_id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  type?: Resolver<ResolversTypes['DataSourceType'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type EnvironmentDataSourceResolvers<ContextType = any, ParentType extends ResolversParentTypes['EnvironmentDataSource'] = ResolversParentTypes['EnvironmentDataSource']> = {
  account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  details?: Resolver<Maybe<ResolversTypes['DataSourceDetails']>, ParentType, ContextType>;
  id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  last_getting_metric_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_getting_metric_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  last_getting_metrics_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  parent_id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  type?: Resolver<ResolversTypes['DataSourceType'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type GcpBillingDataConfigResolvers<ContextType = any, ParentType extends ResolversParentTypes['GcpBillingDataConfig'] = ResolversParentTypes['GcpBillingDataConfig']> = {
  dataset_name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  table_name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type GcpConfigResolvers<ContextType = any, ParentType extends ResolversParentTypes['GcpConfig'] = ResolversParentTypes['GcpConfig']> = {
  billing_data?: Resolver<ResolversTypes['GcpBillingDataConfig'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type GcpDataSourceResolvers<ContextType = any, ParentType extends ResolversParentTypes['GcpDataSource'] = ResolversParentTypes['GcpDataSource']> = {
  account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  config?: Resolver<Maybe<ResolversTypes['GcpConfig']>, ParentType, ContextType>;
  details?: Resolver<Maybe<ResolversTypes['DataSourceDetails']>, ParentType, ContextType>;
  id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  last_getting_metric_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_getting_metric_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  last_getting_metrics_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  parent_id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  type?: Resolver<ResolversTypes['DataSourceType'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type K8CostModelConfigResolvers<ContextType = any, ParentType extends ResolversParentTypes['K8CostModelConfig'] = ResolversParentTypes['K8CostModelConfig']> = {
  cpu_hourly_cost?: Resolver<ResolversTypes['Float'], ParentType, ContextType>;
  memory_hourly_cost?: Resolver<ResolversTypes['Float'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type K8sConfigResolvers<ContextType = any, ParentType extends ResolversParentTypes['K8sConfig'] = ResolversParentTypes['K8sConfig']> = {
  cost_model?: Resolver<Maybe<ResolversTypes['K8CostModelConfig']>, ParentType, ContextType>;
  user?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type K8sDataSourceResolvers<ContextType = any, ParentType extends ResolversParentTypes['K8sDataSource'] = ResolversParentTypes['K8sDataSource']> = {
  account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  config?: Resolver<Maybe<ResolversTypes['K8sConfig']>, ParentType, ContextType>;
  details?: Resolver<Maybe<ResolversTypes['DataSourceDetails']>, ParentType, ContextType>;
  id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  last_getting_metric_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_getting_metric_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  last_getting_metrics_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  parent_id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  type?: Resolver<ResolversTypes['DataSourceType'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type NebiusConfigResolvers<ContextType = any, ParentType extends ResolversParentTypes['NebiusConfig'] = ResolversParentTypes['NebiusConfig']> = {
  access_key_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  bucket_name?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  bucket_prefix?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  cloud_name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  key_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  service_account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type NebiusDataSourceResolvers<ContextType = any, ParentType extends ResolversParentTypes['NebiusDataSource'] = ResolversParentTypes['NebiusDataSource']> = {
  account_id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  config?: Resolver<Maybe<ResolversTypes['NebiusConfig']>, ParentType, ContextType>;
  details?: Resolver<Maybe<ResolversTypes['DataSourceDetails']>, ParentType, ContextType>;
  id?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  last_getting_metric_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_getting_metric_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  last_getting_metrics_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_at?: Resolver<ResolversTypes['Int'], ParentType, ContextType>;
  last_import_attempt_error?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>;
  parent_id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>;
  type?: Resolver<ResolversTypes['DataSourceType'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type QueryResolvers<ContextType = any, ParentType extends ResolversParentTypes['Query'] = ResolversParentTypes['Query']> = {
  dataSource?: Resolver<Maybe<ResolversTypes['DataSourceInterface']>, ParentType, ContextType, RequireFields<QueryDataSourceArgs, 'dataSourceId'>>;
};

export type Resolvers<ContextType = any> = {
  AlibabaConfig?: AlibabaConfigResolvers<ContextType>;
  AlibabaDataSource?: AlibabaDataSourceResolvers<ContextType>;
  AwsConfig?: AwsConfigResolvers<ContextType>;
  AwsDataSource?: AwsDataSourceResolvers<ContextType>;
  AzureSubscriptionConfig?: AzureSubscriptionConfigResolvers<ContextType>;
  AzureSubscriptionDataSource?: AzureSubscriptionDataSourceResolvers<ContextType>;
  AzureTenantConfig?: AzureTenantConfigResolvers<ContextType>;
  AzureTenantDataSource?: AzureTenantDataSourceResolvers<ContextType>;
  DataSourceDetails?: DataSourceDetailsResolvers<ContextType>;
  DataSourceDiscoveryInfos?: DataSourceDiscoveryInfosResolvers<ContextType>;
  DataSourceInterface?: DataSourceInterfaceResolvers<ContextType>;
  DatabricksConfig?: DatabricksConfigResolvers<ContextType>;
  DatabricksDataSource?: DatabricksDataSourceResolvers<ContextType>;
  EnvironmentDataSource?: EnvironmentDataSourceResolvers<ContextType>;
  GcpBillingDataConfig?: GcpBillingDataConfigResolvers<ContextType>;
  GcpConfig?: GcpConfigResolvers<ContextType>;
  GcpDataSource?: GcpDataSourceResolvers<ContextType>;
  K8CostModelConfig?: K8CostModelConfigResolvers<ContextType>;
  K8sConfig?: K8sConfigResolvers<ContextType>;
  K8sDataSource?: K8sDataSourceResolvers<ContextType>;
  NebiusConfig?: NebiusConfigResolvers<ContextType>;
  NebiusDataSource?: NebiusDataSourceResolvers<ContextType>;
  Query?: QueryResolvers<ContextType>;
};

