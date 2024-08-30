import { useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAME = "accessKeyId";

const AccessKeyId = () => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      required
      dataTestId="input_nebius_access_key_id"
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="nebiusAccessKeyIdTooltip"
            messageValues={{
              i: (chunks) => <i>{chunks}</i>
            }}
            dataTestId="qmark_access_key_id`"
          />
        )
      }}
      multiline
      label={intl.formatMessage({ id: "id" }).toUpperCase()}
      autoComplete="off"
    />
  );
};

export default AccessKeyId;
