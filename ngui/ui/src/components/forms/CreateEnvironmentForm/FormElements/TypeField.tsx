import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.RESOURCE_TYPE;

const TypeField = () => (
  <TextInput name={FIELD_NAME} label={<FormattedMessage id="resourceType" />} required dataTestId="input_tag_key" />
);

export default TypeField;
