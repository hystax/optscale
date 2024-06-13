import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { Controller } from "react-hook-form";
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
  AwsRootBillingBucket
} from "components/DataSourceCredentialFields";
import {
  BillingReportBucketDescription,
  BillingReportBucketTitle,
  CloudName,
  ReportBucketName,
  ReportBucketPathPrefix,
  ServiceAccountCredentialsDescription
} from "components/NebiusConfigFormElements";
import QuestionMark from "components/QuestionMark";
import RadioGroupField from "components/RadioGroupField";
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

const IS_FIND_REPORT = "isFindReport";
const CONFIG_SCHEME = "configScheme";

const AwsRootInputs = () => (
  <ConnectForm>
    {({ control, watch }) => {
      const isFindReportWatch = watch(IS_FIND_REPORT, true);
      const configScheme =
        watch(CONFIG_SCHEME, AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT) || AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT;
      return (
        <>
          <AwsRootCredentials />
          <SwitchField
            name={IS_FIND_REPORT}
            defaultValue={isFindReportWatch}
            control={control}
            dataTestIds={{
              labelText: "lbl_use_report",
              input: "checkbox_user_report"
            }}
            labelMessageId="costAndUsageReportDetection"
            endAdornment={
              <QuestionMark
                messageId="costAndUsageReportDetectionTooltip"
                messageValues={{
                  break: <br />
                }}
                dataTestId="qmark_user_report"
              />
            }
          />
          {!isFindReportWatch && (
            <>
              <Controller
                control={control}
                name={CONFIG_SCHEME}
                defaultValue={configScheme}
                render={({ field }) => (
                  <RadioGroupField
                    required
                    fullWidth
                    radioGroupProps={field}
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
                )}
              />
              <Typography gutterBottom data-test-id="p_report_params">
                <FormattedMessage
                  id={
                    configScheme === AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT
                      ? "costAndUsageReportDetectionDescription1"
                      : "costAndUsageReportDetectionDescription2"
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
