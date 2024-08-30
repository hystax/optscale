import { useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../../../constants";

const FIELD_NAME = FIELD_NAMES.AWS_STORAGE.AWS_ACCESS_KEY_ID_FIELD_NAME;

const AwsAccessKeyIdField = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      required
      label={intl.formatMessage({
        id: "awsAccessKeyId"
      })}
      isLoading={isLoading}
    />
  );
};

export default AwsAccessKeyIdField;
