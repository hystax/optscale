import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

const NameField = ({ isLoading = false, readOnly = false }) => (
  <TextInput
    name={FIELD_NAME}
    label={<FormattedMessage id="name" />}
    required
    isLoading={isLoading}
    dataTestId="input_name"
    InputProps={{
      readOnly
    }}
  />
);

export default NameField;
