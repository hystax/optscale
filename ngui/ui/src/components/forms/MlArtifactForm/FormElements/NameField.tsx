import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

const NameField = ({ isLoading = false }) => (
  <TextInput
    name={FIELD_NAME}
    required
    label={<FormattedMessage id="name" />}
    isLoading={isLoading}
    autoFocus
    dataTestId="input_name"
  />
);

export default NameField;
