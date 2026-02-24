import { Box } from "@mui/material";
import {
  AzureTenantCredentials,
  AzureSubscriptionCredentials,
  GcpCredentials,
  GcpTenantCredentials,
  AwsAssumedRoleInputs,
  AlibabaCredentials,
  DatabricksCredentials,
  KubernetesCredentials,
  NebiusCredentials,
} from "components/DataSourceCredentialFields";
import {
  BillingReportBucketDescription,
  BillingReportBucketTitle,
  CloudName,
  ReportBucketName,
  ReportBucketPathPrefix,
  ServiceAccountCredentialsDescription,
} from "components/NebiusConfigFormElements";
import { CONNECTION_TYPES } from "utils/constants";
import { ObjectValues } from "utils/types";
import { AUTHENTICATION_TYPES, AuthenticationType, AwsConnectionAccessKeyInputs } from "./AwsConnectionForm";

const NebiusInputs = () => (
  <>
    <CloudName />
    <Box mt={1} mb={1}>
      <ServiceAccountCredentialsDescription />
    </Box>
    <NebiusCredentials />
    <BillingReportBucketTitle />
    <Box mt={1} mb={1}>
      <BillingReportBucketDescription />
    </Box>
    <ReportBucketName />
    <ReportBucketPathPrefix />
  </>
);

type ConnectionType = ObjectValues<typeof CONNECTION_TYPES>;

const renderAwsInputs = (connectionType: ConnectionType, authenticationType: AuthenticationType | null) => {
  const showAdvancedOptions = connectionType !== CONNECTION_TYPES.AWS_MEMBER;

  return authenticationType === AUTHENTICATION_TYPES.ASSUMED_ROLE ? (
    <AwsAssumedRoleInputs showAssumedRoleCredentialsInModal showAdvancedOptions={showAdvancedOptions} />
  ) : (
    <AwsConnectionAccessKeyInputs showAdvancesOptions={showAdvancedOptions} />
  );
};

const ConnectionInputs = ({
  connectionType,
  authenticationType,
}: {
  connectionType: ConnectionType;
  authenticationType: AuthenticationType | null;
}) => {
  switch (connectionType) {
    case CONNECTION_TYPES.AWS_MANAGEMENT:
    case CONNECTION_TYPES.AWS_MEMBER:
      return renderAwsInputs(connectionType, authenticationType);
    case CONNECTION_TYPES.AZURE_TENANT:
      return <AzureTenantCredentials />;
    case CONNECTION_TYPES.AZURE_SUBSCRIPTION:
      return <AzureSubscriptionCredentials />;
    case CONNECTION_TYPES.GCP_PROJECT:
      return <GcpCredentials />;
    case CONNECTION_TYPES.GCP_TENANT:
      return <GcpTenantCredentials />;
    case CONNECTION_TYPES.ALIBABA:
      return <AlibabaCredentials />;
    case CONNECTION_TYPES.NEBIUS:
      return <NebiusInputs />;
    case CONNECTION_TYPES.DATABRICKS:
      return <DatabricksCredentials />;
    case CONNECTION_TYPES.KUBERNETES:
      return <KubernetesCredentials />;
    default:
      return null;
  }
};

export default ConnectionInputs;
