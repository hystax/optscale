import { useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../../../constants";

const FIELD_NAME = FIELD_NAMES.AZURE_STORAGE.CONNECTION_STRING_FIELD_NAME;

const ConnectionStringField = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={intl.formatMessage({ id: "connectionString" })}
      required
      isLoading={isLoading}
      dataTestId="input_connection_string"
    />
  );
};

export default ConnectionStringField;
