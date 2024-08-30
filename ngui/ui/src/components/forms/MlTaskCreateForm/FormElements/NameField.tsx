import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

const MlTaskCreateFormNameField = () => (
  <TextInput name={FIELD_NAME} label={<FormattedMessage id="name" />} dataTestId="input_name" required autoFocus />
);

export default MlTaskCreateFormNameField;
