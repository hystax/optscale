import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import ConnectForm from "components/ConnectForm";
import {
  AlibabaCredentials,
  AwsRootCredentials,
  AwsLinkedCredentials,
  AzureTenantCredentials,
  AzureSubscriptionCredentials,
  NebiusCredentials,
  GcpCredentials,
  KubernetesCredentials,
  DatabricksCredentials,
  AwsRootBillingBucket,
  AwsRootExportType,
  AwsRootUseAwsEdpDiscount
} from "components/DataSourceCredentialFields";
import { RadioGroup } from "components/forms/common/fields";
import {
  BillingReportBucketDescription,
  BillingReportBucketTitle,
  CloudName,
  ReportBucketName,
  ReportBucketPathPrefix,
  ServiceAccountCredentialsDescription
} from "components/NebiusConfigFormElements";
import QuestionMark from "components/QuestionMark";
import SwitchField from "components/SwitchField";
import {
  AWS_ROOT_CONNECT_CONFIG_SCHEMES,
  AWS_ROOT_ACCOUNT,
  AWS_LINKED_ACCOUNT,
  AZURE_SUBSCRIPTION,
  AZURE_TENANT_ACCOUNT,
  KUBERNETES,
  ALIBABA_ACCOUNT,
  GCP_ACCOUNT,
  NEBIUS_ACCOUNT,
  DATABRICKS_ACCOUNT
} from "utils/constants";

export const AWS_ROOT_INPUTS_FIELD_NAMES = {
  IS_FIND_REPORT: "isFindReport",
  CONFIG_SCHEME: "configScheme"
};

const AwsRootInputs = () => (
  <ConnectForm>
    {({ control, watch }) => {
      const isFindReportWatch = watch(AWS_ROOT_INPUTS_FIELD_NAMES.IS_FIND_REPORT, true);
      const configScheme =
        watch(AWS_ROOT_INPUTS_FIELD_NAMES.CONFIG_SCHEME, AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT) ||
        AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT;
      return (
        <>
          <AwsRootCredentials />
          <AwsRootUseAwsEdpDiscount />
          <AwsRootExportType />
          <SwitchField
            name={AWS_ROOT_INPUTS_FIELD_NAMES.IS_FIND_REPORT}
            defaultValue={isFindReportWatch}
            control={control}
            dataTestIds={{
              labelText: "lbl_data_export_detection",
              input: "switch_data_export_detection"
            }}
            labelMessageId="dataExportDetection"
            endAdornment={
              <QuestionMark
                messageId="dataExportDetectionTooltip"
                messageValues={{
                  break: <br />
                }}
                dataTestId="qmark_user_report"
              />
            }
          />
          {!isFindReportWatch && (
            <>
              <RadioGroup
                name={AWS_ROOT_INPUTS_FIELD_NAMES.CONFIG_SCHEME}
                defaultValue={configScheme}
                radioButtons={[
                  {
                    value: AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT,
                    label: <FormattedMessage id="createNewCostUsageReport" />
                  },
                  {
                    value: AWS_ROOT_CONNECT_CONFIG_SCHEMES.BUCKET_ONLY,
                    label: <FormattedMessage id="connectOnlyToDataInBucket" />
                  }
                ]}
              />
              <Typography gutterBottom data-test-id="p_data_export_detection_description">
                <FormattedMessage
                  id={
                    configScheme === AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT
                      ? "dataExportDetectionDescription1"
                      : "dataExportDetectionDescription2"
                  }
                />
              </Typography>
              <AwsRootBillingBucket />
            </>
          )}
        </>
      );
    }}
  </ConnectForm>
);

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

const ConnectionInputs = ({ connectionType }) => {
  switch (connectionType) {
    case AWS_ROOT_ACCOUNT:
      return <AwsRootInputs />;
    case AWS_LINKED_ACCOUNT:
      return <AwsLinkedCredentials />;
    case AZURE_TENANT_ACCOUNT:
      return <AzureTenantCredentials />;
    case AZURE_SUBSCRIPTION:
      return <AzureSubscriptionCredentials />;
    case ALIBABA_ACCOUNT:
      return <AlibabaCredentials />;
    case GCP_ACCOUNT:
      return <GcpCredentials />;
    case NEBIUS_ACCOUNT:
      return <NebiusInputs />;
    case DATABRICKS_ACCOUNT:
      return <DatabricksCredentials />;
    case KUBERNETES:
      return <KubernetesCredentials />;
    default:
      return null;
  }
};

export default ConnectionInputs;
