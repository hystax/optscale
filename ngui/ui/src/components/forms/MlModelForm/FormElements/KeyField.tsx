import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.KEY;

const KeyField = ({ isLoading = false }) => (
  <TextInput name={FIELD_NAME} label={<FormattedMessage id="key" />} required isLoading={isLoading} dataTestId="input_key" />
);

export default KeyField;
