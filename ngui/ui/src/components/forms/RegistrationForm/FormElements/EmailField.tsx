import { FormattedMessage, useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { emailRegex } from "utils/strings";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.EMAIL;

const EmailField = ({ readOnly = false }) => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      required
      dataTestId="input_email"
      label={<FormattedMessage id="businessLogin" />}
      type="email"
      autoComplete="username email"
      margin="normal"
      InputProps={{
        readOnly
      }}
      pattern={{
        value: emailRegex,
        message: intl.formatMessage({ id: "invalidEmailAddress" })
      }}
    />
  );
};

export default EmailField;
