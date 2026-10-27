import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import AwsAssumedRoleCredentials from "../AwsAssumedRoleCredentials";
import AwsBillingBucketInputs from "../AwsBillingBucketInputs";
import AwsExportType from "../AwsExportType";
import AwsRegionScope from "../AwsRegionScope";
import AwsUseAwsEdpDiscount from "../AwsUseAwsEdpDiscount";

const AwsAssumedRoleInputs = ({
  readOnlyFields = [],
  hiddenFields = [],
  showAssumedRoleCredentialsInModal = false,
  showAdvancedOptions = true,
  showExternalIdToggle = false,
}: {
  readOnlyFields?: string[];
  hiddenFields?: string[];
  showAssumedRoleCredentialsInModal?: boolean;
  showAdvancedOptions?: boolean;
  showExternalIdToggle?: boolean;
}) => (
  <>
    <AwsAssumedRoleCredentials
      readOnlyFields={readOnlyFields}
      hiddenFields={hiddenFields}
      showExternalIdToggle={showExternalIdToggle}
    />
    <AwsRegionScope />
    {showAdvancedOptions && (
      <>
        <AwsUseAwsEdpDiscount />
        <Typography gutterBottom data-test-id="p_cost_and_usage_report_parameters_description">
          <FormattedMessage id="costAndUsageReportParametersDescription" />
        </Typography>
        <AwsExportType />
        <AwsBillingBucketInputs showAssumedRoleCredentialsInModal={showAssumedRoleCredentialsInModal} />
      </>
    )}
  </>
);

export default AwsAssumedRoleInputs;
