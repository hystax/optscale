import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.PATH;

const IdField = ({ isLoading = false, autoFocus = false }) => (
  <TextInput
    name={FIELD_NAME}
    dataTestId="input_id"
    label={<FormattedMessage id="id" />}
    required
    isLoading={isLoading}
    autoFocus={autoFocus}
  />
);

export default IdField;
