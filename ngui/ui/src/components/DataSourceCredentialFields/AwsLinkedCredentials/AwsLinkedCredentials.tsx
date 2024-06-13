import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAMES = Object.freeze({
  ACCESS_KEY_ID: "awsAccessKeyId",
  SECRET_ACCESS_KEY: "awsSecretAccessKey"
});

const AwsLinkedCredentials = () => (
  <>
    <TextInput
      name={FIELD_NAMES.ACCESS_KEY_ID}
      required
      dataTestId="input_aws_access_key_id"
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="awsAccessKeyIdTooltip"
            messageValues={{
              i: (chunks) => <i>{chunks}</i>
            }}
            dataTestId="qmark_access_key"
          />
        )
      }}
      label={<FormattedMessage id="awsAccessKeyId" />}
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
            messageId="awsSecretAccessKeyTooltip"
            messageValues={{
              i: (chunks) => <i>{chunks}</i>
            }}
            dataTestId="qmark_secret_key"
          />
        )
      }}
      label={<FormattedMessage id="awsSecretAccessKey" />}
      autoComplete="off"
    />
  </>
);

export default AwsLinkedCredentials;
