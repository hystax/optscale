import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

const NameField = () => (
  <TextInput name={FIELD_NAME} required dataTestId="input_cloud_account_name" label={<FormattedMessage id="name" />} />
);

export default NameField;
