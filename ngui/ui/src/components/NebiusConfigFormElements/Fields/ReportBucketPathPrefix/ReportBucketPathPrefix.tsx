import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAME = "bucketPrefix";

const ReportBucketPathPrefix = ({ disabled = false }) => (
  <TextInput
    name={FIELD_NAME}
    dataTestId="input_nebius_report_path_prefix"
    disabled={disabled}
    InputProps={{
      endAdornment: (
        <QuestionMark
          messageId="nebiusReportPathPrefixTooltip"
          messageValues={{
            i: (chunks) => <i>{chunks}</i>
          }}
          dataTestId="qmark_report_path_prefix"
        />
      )
    }}
    label={<FormattedMessage id="pathPrefix" />}
    autoComplete="off"
  />
);

export default ReportBucketPathPrefix;
