import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAMES = Object.freeze({
  ACCESS_KEY_ID: "alibabaAccessKeyId",
  SECRET_ACCESS_KEY: "alibabaSecretAccessKey"
});

const AlibabaCredentials = () => (
  <>
    <TextInput
      name={FIELD_NAMES.ACCESS_KEY_ID}
      required
      dataTestId="input_alibaba_access_key_id"
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="alibabaAccessKeyIdTooltip"
            messageValues={{
              i: (chunks) => <i>{chunks}</i>
            }}
            dataTestId="qmark_access_key"
          />
        )
      }}
      label={<FormattedMessage id="alibabaAccessKeyId" />}
      autoComplete="off"
    />
    <TextInput
      name={FIELD_NAMES.SECRET_ACCESS_KEY}
      required
      masked
      dataTestId="input_secret_key"
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="alibabaSecretAccessKeyTooltip"
            messageValues={{
              i: (chunks) => <i>{chunks}</i>
            }}
            dataTestId="qmark_secret_key"
          />
        )
      }}
      label={<FormattedMessage id="alibabaSecretAccessKey" />}
      autoComplete="off"
    />
  </>
);

export default AlibabaCredentials;
