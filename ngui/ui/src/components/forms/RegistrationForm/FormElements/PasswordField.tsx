import { FormattedMessage } from "react-intl";
import { PasswordInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.PASSWORD;

const PasswordField = () => (
  <PasswordInput
    name={FIELD_NAME}
    required
    dataTestId="input_pass"
    label={<FormattedMessage id="password" />}
    margin="normal"
    autoComplete="new-password"
    minLength={6}
  />
);

export default PasswordField;
