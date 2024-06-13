import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

const MlEditTaskFormNameField = () => (
  <TextInput name={FIELD_NAME} dataTestId="input_name" label={<FormattedMessage id="name" />} required autoFocus />
);

export default MlEditTaskFormNameField;
