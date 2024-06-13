import { useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAME = "keyId";

const AuthorizedKeyId = () => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      required
      dataTestId="input_nebius_authorized_key_id"
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="nebiusAuthorizedKeyIdTooltip"
            messageValues={{
              i: (chunks) => <i>{chunks}</i>
            }}
            dataTestId="qmark_authorized_key_id"
          />
        )
      }}
      label={intl.formatMessage({ id: "id" }).toUpperCase()}
      autoComplete="off"
    />
  );
};

export default AuthorizedKeyId;
