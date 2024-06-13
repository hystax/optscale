import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

const NameField = () => <TextInput name={FIELD_NAME} label="name" required autoFocus dataTestId="input_chart_name" />;

export default NameField;
