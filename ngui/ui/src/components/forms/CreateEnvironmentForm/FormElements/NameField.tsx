import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

const NameField = () => (
  <TextInput name={FIELD_NAME} label={<FormattedMessage id={FIELD_NAME} />} required autoFocus dataTestId="input_name" />
);

export default NameField;
