import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAME = "bucketName";

const ReportBucketName = ({ disabled = false }) => (
  <TextInput
    name={FIELD_NAME}
    required
    dataTestId="input_nebius_report_bucket_name"
    disabled={disabled}
    InputProps={{
      endAdornment: (
        <QuestionMark
          messageId="nebiusReportBucketNameTooltip"
          messageValues={{
            i: (chunks) => <i>{chunks}</i>
          }}
          dataTestId="qmark_report_bucket_name"
        />
      )
    }}
    label={<FormattedMessage id="bucketName" />}
    autoComplete="off"
  />
);

export default ReportBucketName;
