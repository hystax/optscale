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
      label={<FormattedMessage id="userLogin" />}
      required
      InputProps={{
        readOnly
      }}
      type="email"
      autoComplete="email"
      dataTestId="input_email"
      margin="normal"
      pattern={{
        value: emailRegex,
        message: intl.formatMessage({ id: "invalidEmailAddress" })
      }}
    />
  );
};

export default EmailField;
