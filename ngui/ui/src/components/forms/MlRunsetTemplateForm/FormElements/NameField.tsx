import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

export const FIELD_NAME = FIELD_NAMES.NAME; // "name";

const NameField = ({ isLoading = false }) => (
  <TextInput
    name={FIELD_NAME}
    dataTestId="input_name"
    label={<FormattedMessage id="name" />}
    required
    autoFocus
    isLoading={isLoading}
  />
);

export default NameField;
