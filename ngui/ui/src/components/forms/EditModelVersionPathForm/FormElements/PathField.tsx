import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.PATH;

const EditModelVersionPathFormPathField = () => (
  <TextInput name={FIELD_NAME} autoFocus label={<FormattedMessage id="path" />} dataTestId={`input_${FIELD_NAME}`} />
);

export default EditModelVersionPathFormPathField;
