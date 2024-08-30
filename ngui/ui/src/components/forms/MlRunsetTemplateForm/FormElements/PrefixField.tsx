import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

export const FIELD_NAME = FIELD_NAMES.RESOURCE_NAME_PREFIX; // "resourceNamePrefix";

const PrefixField = ({ isLoading = false }) => (
  <TextInput
    name={FIELD_NAME}
    dataTestId="input_resource_name_prefix"
    label={<FormattedMessage id="resourceNamePrefix" />}
    required
    isLoading={isLoading}
  />
);

export default PrefixField;
