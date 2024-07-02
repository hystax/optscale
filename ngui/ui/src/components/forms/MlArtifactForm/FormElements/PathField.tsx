import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.PATH;

const PathField = ({ isLoading = false }) => (
  <TextInput name={FIELD_NAME} dataTestId="input_path" label={<FormattedMessage id="path" />} required isLoading={isLoading} />
);

export default PathField;
