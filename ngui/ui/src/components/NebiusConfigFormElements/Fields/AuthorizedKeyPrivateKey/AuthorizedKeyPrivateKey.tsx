import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAME = "privateKey";

const AuthorizedKeyPrivateKey = () => (
  <TextInput
    name={FIELD_NAME}
    required
    dataTestId="input_nebius_private_authorized_key"
    InputProps={{
      endAdornment: (
        <QuestionMark
          messageId="nebiusPrivateAuthorizedKeyTooltip"
          messageValues={{
            i: (chunks) => <i>{chunks}</i>
          }}
          dataTestId="qmark_private_authorized_key"
        />
      )
    }}
    multiline
    minRows={4}
    label={<FormattedMessage id="privateKey" />}
    autoComplete="off"
    sx={{
      marginBottom: (theme) => theme.spacing(1)
    }}
  />
);

export default AuthorizedKeyPrivateKey;
