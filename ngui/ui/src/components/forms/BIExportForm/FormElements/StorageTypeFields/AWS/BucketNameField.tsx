import { useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../../../constants";

const FIELD_NAME = FIELD_NAMES.AWS_STORAGE.BUCKET_NAME_FIELD_NAME;

const BucketNameField = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={intl.formatMessage({ id: "bucketName" })}
      required
      isLoading={isLoading}
      dataTestId="input_s3_bucket_name"
    />
  );
};

export default BucketNameField;
