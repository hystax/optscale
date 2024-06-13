import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../utils";

const NameField = ({ name = FIELD_NAMES.NAME, isLoading = false }) => (
  <TextInput
    name={name}
    margin="normal"
    dataTestId="input_name"
    label={<FormattedMessage id="name" />}
    required
    autoFocus
    isLoading={isLoading}
  />
);

export default NameField;
