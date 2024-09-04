import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.EMAIL;

/**
 * Email field is required to let the browser know which account the user is trying to reset the password for.
 * https://www.chromium.org/developers/design-documents/create-amazing-password-forms/#use-hidden-fields-for-implicit-information
 */
const EmailField = () => (
  <TextInput
    name={FIELD_NAME}
    label={<FormattedMessage id="userLogin" />}
    required
    InputProps={{
      readOnly: true
    }}
    type="email"
    autoComplete="email"
    dataTestId="input_email"
    margin="normal"
  />
);

export default EmailField;
