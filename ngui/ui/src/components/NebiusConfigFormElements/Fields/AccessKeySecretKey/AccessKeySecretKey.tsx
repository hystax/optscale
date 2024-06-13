import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAME = "secretAccessKey";

const AccessKeySecretKey = () => (
  <TextInput
    name={FIELD_NAME}
    required
    dataTestId="input_nebius_secret_access_key"
    InputProps={{
      endAdornment: (
        <QuestionMark
          messageId="nebiusSecretAccessKeyTooltip"
          messageValues={{
            i: (chunks) => <i>{chunks}</i>
          }}
          dataTestId="qmark_secret_access_key"
        />
      )
    }}
    label={<FormattedMessage id="secretKey" />}
    autoComplete="off"
    sx={{
      marginBottom: (theme) => theme.spacing(1)
    }}
  />
);

export default AccessKeySecretKey;
