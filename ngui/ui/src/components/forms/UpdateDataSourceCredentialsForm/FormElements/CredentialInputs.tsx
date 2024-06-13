import { Box, FormControlLabel, Switch, Typography } from "@mui/material";
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
  AwsRootBillingBucket
} from "components/DataSourceCredentialFields";
import {
  BillingReportBucketTitle,
  CloudName,
  ReportBucketName,
  ReportBucketPathPrefix
} from "components/NebiusConfigFormElements";
import UpdateServiceAccountCredentialsDescription from "components/NebiusConfigFormElements/UpdateServiceAccountCredentialsDescription";
import { useToggle } from "hooks/useToggle";
import { ALIBABA_CNR, AZURE_TENANT, AWS_CNR, AZURE_CNR, NEBIUS, GCP_CNR, DATABRICKS, KUBERNETES_CNR } from "utils/constants";

const CostAndUsageReport = () => {
  const [checked, toggleChecked] = useToggle(false);

  return (
    <>
      <FormControlLabel
        control={<Switch checked={checked} onChange={toggleChecked} inputProps={{ "aria-label": "switch" }} />}
        label={
          <Box display="flex" alignItems="center">
            <Typography>
              <FormattedMessage id="updateCostAndUsageReportParameters" />
            </Typography>
          </Box>
        }
        labelPlacement="end"
      />
      {checked && <AwsRootBillingBucket />}
    </>
  );
};

const CredentialInputs = ({ type, config }) => {
  switch (type) {
    case AWS_CNR:
      return config.linked ? (
        <AwsLinkedCredentials />
      ) : (
        <>
          <AwsRootCredentials />
          <CostAndUsageReport />
        </>
      );
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
            GCP_CREDENTIALS_FIELD_NAMES.PROJECT_ID
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
