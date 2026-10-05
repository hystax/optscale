import { ReactNode } from "react";

export type K8sPropertiesProps = {
  id: string;
  accountId: string;
  config: K8sConfig;
  createdAt: string;
};

export type K8sConfig = {
  user: string;
  custom_price: boolean;
  cost_model: K8sConstModel;
};

type K8sConstModel = {
  cpu_hourly_cost: number;
  memory_hourly_cost: number;
};

type BasePropertiesProps = {
  accountId: string;
  createdAt: string;
};

export type GcpPropertiesProps = BasePropertiesProps & {
  config: {
    billing_data?: {
      dataset_name?: string;
      table_name?: string;
      project_id?: string;
    };
    pricing_data?: {
      dataset_name?: string;
      table_name?: string;
      project_id?: string;
    };
  };
};

export type AlibabaPropertiesProps = BasePropertiesProps & {
  config: {
    access_key_id: string;
  };
};

export type AwsPropertiesProps = BasePropertiesProps & {
  lastImportFromCloudAccountId?: string | null;
  lastImportFromAwsAccountId?: string | null;
  config: {
    createdAt: number;
    access_key_id: string;
    assume_role_account_id: string;
    assume_role_name: string;
    assume_role_external_id?: string;
    bucket_name: string;
    bucket_prefix: string;
    linked: boolean;
    report_name: string;
    config_scheme?: string;
    region_name?: string;
    cur_version?: 1 | 2;
    use_edp_discount?: boolean;
    included_regions?: string[];
    excluded_regions?: string[];
  };
};

export type AzurePropertiesProps = {
  createdAt: string;
  parentId?: string | null;
  config: {
    client_id: string;
    tenant: string;
    expense_import_scheme: string;
    subscription_id?: string;
    export_name?: string;
    container: ReactNode;
    directory: ReactNode;
  };
};

export type DatabricksPropertiesProps = BasePropertiesProps & {
  config: {
    client_id: string;
  };
};

export type NebiusPropertiesProps = BasePropertiesProps & {
  config: {
    cloud_name: string;
    service_account_id: string;
    key_id: string;
    access_key_id: string;
    bucket_name: string;
    bucket_prefix: string;
  };
};
