import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.ORGANIZATION_NAME;

const OrganizationNameField = () => (
  <TextInput
    name={FIELD_NAME}
    label={<FormattedMessage id="name" />}
    required
    maxLength={DEFAULT_MAX_INPUT_LENGTH}
    margin="none"
  />
);

export default OrganizationNameField;
