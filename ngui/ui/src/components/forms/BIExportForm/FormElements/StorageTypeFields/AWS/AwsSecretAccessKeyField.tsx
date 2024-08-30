import { useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../../../constants";

const FIELD_NAME = FIELD_NAMES.AWS_STORAGE.AWS_SECRET_ACCESS_KEY_FIELD_NAME;

const AwsSecretAccessKeyField = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={intl.formatMessage({ id: "awsSecretAccessKey" })}
      required
      masked
      isLoading={isLoading}
      dataTestId="input_aws_secret_key"
      autoComplete="off"
    />
  );
};

export default AwsSecretAccessKeyField;
