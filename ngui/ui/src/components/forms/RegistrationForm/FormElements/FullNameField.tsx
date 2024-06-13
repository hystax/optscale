import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.FULL_NAME;

const FULL_NAME_MAX_LENGTH = 64;

const FullNameField = () => (
  <TextInput
    name={FIELD_NAME}
    required
    dataTestId="input_email"
    label={<FormattedMessage id="fullName" />}
    margin="normal"
    autoComplete="name"
    maxLength={FULL_NAME_MAX_LENGTH}
  />
);

export default FullNameField;
