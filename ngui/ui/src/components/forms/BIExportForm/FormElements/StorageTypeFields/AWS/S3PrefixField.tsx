import { useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../../../constants";

const FIELD_NAME = FIELD_NAMES.AWS_STORAGE.S3_PATH_FIELD_NAME;

const S3PrefixField = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={intl.formatMessage({ id: "s3Prefix" })}
      required
      isLoading={isLoading}
      dataTestId="input_s3_prefix"
    />
  );
};

export default S3PrefixField;
