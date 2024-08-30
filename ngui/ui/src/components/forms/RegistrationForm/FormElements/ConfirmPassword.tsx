import { FormattedMessage, useIntl } from "react-intl";
import { PasswordInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.CONFIRM_PASSWORD;

const ConfirmPassword = () => {
  const intl = useIntl();

  return (
    <PasswordInput
      name={FIELD_NAME}
      required
      dataTestId="input_conf_pass"
      label={<FormattedMessage id="confirmPassword" />}
      margin="normal"
      autoComplete="new-password"
      validate={{
        match: (value, formValues) => value === formValues.password || intl.formatMessage({ id: "passwordsDoNotMatch" })
      }}
    />
  );
};

export default ConfirmPassword;
