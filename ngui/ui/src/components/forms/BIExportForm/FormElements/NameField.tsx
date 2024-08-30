import { useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

const NameField = ({ isLoading = false }) => {
  const intl = useIntl();

  return <TextInput name={FIELD_NAME} label={intl.formatMessage({ id: "name" })} required autoFocus isLoading={isLoading} />;
};

export default NameField;
