import { useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../../../constants";

const FIELD_NAME = FIELD_NAMES.AZURE_STORAGE.CONTAINER_FIELD_NAME;

const ContainerField = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={intl.formatMessage({ id: "container" })}
      required
      isLoading={isLoading}
      dataTestId="input_container"
    />
  );
};

export default ContainerField;
