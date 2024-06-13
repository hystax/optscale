import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const NAME_MAX_SIZE = 30;

const FIELD_NAME = FIELD_NAMES.NAME;

const NameField = () => (
  <TextInput
    name={FIELD_NAME}
    label={<FormattedMessage id="name" />}
    required
    autoFocus
    dataTestId="input_name"
    maxLength={NAME_MAX_SIZE}
  />
);

export default NameField;
