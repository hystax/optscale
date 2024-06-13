import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.KEY;

const KeyField = () => <TextInput name={FIELD_NAME} label={<FormattedMessage id="key" />} required dataTestId="input_name" />;

export default KeyField;
