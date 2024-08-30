import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAME = "cloudName";

const CloudName = ({ disabled = false }) => (
  <TextInput
    name={FIELD_NAME}
    required
    dataTestId="input_nebius_cloud_name"
    disabled={disabled}
    InputProps={{
      endAdornment: (
        <QuestionMark
          messageId="nebiusCloudNameTooltip"
          messageValues={{
            i: (chunks) => <i>{chunks}</i>
          }}
          dataTestId="qmark_cloud_name"
        />
      )
    }}
    label={<FormattedMessage id="cloudName" />}
    autoComplete="off"
  />
);

export default CloudName;
