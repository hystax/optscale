import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

const MlModelFormNameField = ({ isLoading = false }) => (
  <TextInput
    name={FIELD_NAME}
    label={<FormattedMessage id="name" />}
    required
    autoFocus
    isLoading={isLoading}
    dataTestId="input_name"
  />
);

export default MlModelFormNameField;
