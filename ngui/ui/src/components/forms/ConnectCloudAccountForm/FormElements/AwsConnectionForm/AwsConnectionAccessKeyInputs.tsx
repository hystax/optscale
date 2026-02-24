import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import ConnectForm from "components/ConnectForm";
import {
  AwsBillingBucket,
  AwsExportType,
  AwsRootCredentials,
  AwsUseAwsEdpDiscount,
} from "components/DataSourceCredentialFields";
import { RadioGroup, Switch } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { AWS_ROOT_CONNECT_CONFIG_SCHEMES } from "utils/constants";
import { AWS_ROOT_INPUTS_FIELD_NAMES } from "./constants";

export const AwsConnectionAccessKeyInputs = ({ showAdvancesOptions = true }) => (
  <ConnectForm>
    {({ watch }) => {
      const isFindReportWatch = watch(AWS_ROOT_INPUTS_FIELD_NAMES.IS_FIND_REPORT, true);
      const configScheme =
        watch(AWS_ROOT_INPUTS_FIELD_NAMES.CONFIG_SCHEME, AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT) ||
        AWS_ROOT_CONNECT_CONFIG_SCHEMES.CREATE_REPORT;
      return (
        <>
          <AwsRootCredentials />
          {showAdvancesOptions && (
            <>
              <AwsUseAwsEdpDiscount />
              <AwsExportType />
              <Switch
                name={AWS_ROOT_INPUTS_FIELD_NAMES.IS_FIND_REPORT}
                label={<FormattedMessage id="dataExportDetection" />}
                defaultValue={isFindReportWatch}
                adornment={
                  <QuestionMark
                    messageId="dataExportDetectionTooltip"
                    messageValues={{
                      break: <br />,
                    }}
                    dataTestId="qmark_data_export_detection"
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
                        label: <FormattedMessage id="createNewCostUsageReport" />,
                      },
                      {
                        value: AWS_ROOT_CONNECT_CONFIG_SCHEMES.BUCKET_ONLY,
                        label: <FormattedMessage id="connectOnlyToDataInBucket" />,
                      },
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
                  <AwsBillingBucket />
                </>
              )}
            </>
          )}
        </>
      );
    }}
  </ConnectForm>
);
