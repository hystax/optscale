import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.CODE;

const CodeField = () => <TextInput name={FIELD_NAME} required label={<FormattedMessage id="code" />} />;

export default CodeField;
