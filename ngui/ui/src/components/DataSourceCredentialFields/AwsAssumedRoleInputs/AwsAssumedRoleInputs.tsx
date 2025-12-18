import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import AwsAssumedRoleCredentials from "../AwsAssumedRoleCredentials";
import AwsBillingBucketInputs from "../AwsBillingBucketInputs";
import AwsExportType from "../AwsExportType";
import AwsUseAwsEdpDiscount from "../AwsUseAwsEdpDiscount";

const AwsAssumedRoleInputs = ({
  readOnlyFields = [],
  showAssumedRoleCredentialsInModal = false
}: {
  readOnlyFields?: string[];
  showAssumedRoleCredentialsInModal?: boolean;
}) => (
  <>
    <AwsAssumedRoleCredentials readOnlyFields={readOnlyFields} />
    <AwsUseAwsEdpDiscount />
    <Typography gutterBottom data-test-id="p_cost_and_usage_report_parameters_description">
      <FormattedMessage id="costAndUsageReportParametersDescription" />
    </Typography>
    <AwsExportType />
    <AwsBillingBucketInputs showAssumedRoleCredentialsInModal={showAssumedRoleCredentialsInModal} />
  </>
);

export default AwsAssumedRoleInputs;
