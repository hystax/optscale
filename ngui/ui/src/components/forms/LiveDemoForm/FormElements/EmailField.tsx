import { FormattedMessage, useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { emailRegex } from "utils/strings";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.EMAIL;

const EmailField = () => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={<FormattedMessage id="email" />}
      required
      dataTestId="input_email"
      pattern={{
        value: emailRegex,
        message: intl.formatMessage({ id: "invalidEmailAddress" })
      }}
    />
  );
};

export default EmailField;
