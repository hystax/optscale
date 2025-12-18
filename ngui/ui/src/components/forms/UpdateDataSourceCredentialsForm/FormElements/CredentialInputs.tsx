import { Box, Typography } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import {
  AlibabaCredentials,
  AzureTenantCredentials,
  AzureSubscriptionCredentials,
  AZURE_TENANT_CREDENTIALS_FIELD_NAMES,
  AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES,
  NebiusCredentials,
  GcpCredentials,
  GCP_CREDENTIALS_FIELD_NAMES,
  DATABRICKS_CREDENTIALS_FIELD_NAMES,
  DatabricksCredentials,
  KubernetesCredentials,
  AwsLinkedCredentials,
  AwsRootCredentials,
  AwsBillingBucket,
  AwsExportType,
  AwsUseAwsEdpDiscount,
  GcpTenantCredentials,
  GCP_TENANT_CREDENTIALS_FIELD_NAMES,
  AwsAssumedRoleInputs,
  AWS_ROLE_CREDENTIALS_FIELD_NAMES
} from "components/DataSourceCredentialFields";
import { Switch } from "components/forms/common/fields";
import {
  BillingReportBucketTitle,
  CloudName,
  ReportBucketName,
  ReportBucketPathPrefix
} from "components/NebiusConfigFormElements";
import UpdateServiceAccountCredentialsDescription from "components/NebiusConfigFormElements/UpdateServiceAccountCredentialsDescription";
import {
  ALIBABA_CNR,
  AZURE_TENANT,
  AWS_CNR,
  AZURE_CNR,
  NEBIUS,
  GCP_CNR,
  DATABRICKS,
  KUBERNETES_CNR,
  GCP_TENANT
} from "utils/constants";

export const AWS_POOL_UPDATE_DATA_EXPORT_PARAMETERS = "updateDataExportParameters";

const CostAndUsageReport = () => {
  const { watch } = useFormContext();

  const checked = watch(AWS_POOL_UPDATE_DATA_EXPORT_PARAMETERS);

  return (
    <>
      <Switch
        name={AWS_POOL_UPDATE_DATA_EXPORT_PARAMETERS}
        label={
          <Typography>
            <FormattedMessage id="updateDataExportParameters" />
          </Typography>
        }
      />
      {checked && (
        <>
          <AwsExportType />
          <AwsBillingBucket />
        </>
      )}
    </>
  );
};

const CredentialInputs = ({ type, config }) => {
  const getAwsInputs = (config) => {
    if (config.linked) {
      return <AwsLinkedCredentials />;
    }

    if (config.assume_role_account_id && config.assume_role_name) {
      return <AwsAssumedRoleInputs readOnlyFields={[AWS_ROLE_CREDENTIALS_FIELD_NAMES.ASSUME_ROLE_ACCOUNT_ID]} />;
    }

    return (
      <>
        <AwsRootCredentials />
        <AwsUseAwsEdpDiscount />
        <CostAndUsageReport />
      </>
    );
  };

  switch (type) {
    case AWS_CNR:
      return getAwsInputs(config);
    case AZURE_TENANT:
      return <AzureTenantCredentials readOnlyFields={[AZURE_TENANT_CREDENTIALS_FIELD_NAMES.TENANT]} />;
    case AZURE_CNR:
      return (
        <AzureSubscriptionCredentials
          hiddenFields={[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.SUBSCRIPTION_ID]}
          readOnlyFields={[AZURE_SUBSCRIPTION_CREDENTIALS_FIELD_NAMES.TENANT]}
        />
      );
    case ALIBABA_CNR:
      return <AlibabaCredentials />;
    case DATABRICKS:
      return <DatabricksCredentials readOnlyFields={[DATABRICKS_CREDENTIALS_FIELD_NAMES.ACCOUNT_ID]} />;
    case KUBERNETES_CNR:
      return <KubernetesCredentials />;
    case GCP_CNR:
      return (
        <GcpCredentials
          hidden={[
            GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_DATASET,
            GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_TABLE,
            GCP_CREDENTIALS_FIELD_NAMES.BILLING_DATA_PROJECT_ID
          ]}
        />
      );
    case GCP_TENANT:
      return (
        <GcpTenantCredentials
          hidden={[
            GCP_TENANT_CREDENTIALS_FIELD_NAMES.BILLING_DATA_DATASET,
            GCP_TENANT_CREDENTIALS_FIELD_NAMES.BILLING_DATA_TABLE
          ]}
        />
      );
    case NEBIUS:
      return (
        <>
          <CloudName disabled />
          <Box mt={1} mb={1}>
            <UpdateServiceAccountCredentialsDescription />
          </Box>
          <NebiusCredentials />
          <BillingReportBucketTitle />
          <ReportBucketName disabled />
          <ReportBucketPathPrefix disabled />
        </>
      );
    default:
      return null;
  }
};

export default CredentialInputs;
