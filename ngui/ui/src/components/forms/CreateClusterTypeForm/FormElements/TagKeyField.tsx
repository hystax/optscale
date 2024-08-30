import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.TAG_KEY;

const TagKeyField = () => (
  <TextInput name={FIELD_NAME} label={<FormattedMessage id="tagKey" />} required dataTestId="input_tag_key" />
);

export default TagKeyField;
