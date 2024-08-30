import { FormattedMessage } from "react-intl";
import { PasswordInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.PASSWORD;

const PasswordField = () => (
  <PasswordInput
    name={FIELD_NAME}
    required
    label={<FormattedMessage id="password" />}
    autoComplete="current-password"
    margin="normal"
    dataTestId="input_pass"
  />
);

export default PasswordField;
