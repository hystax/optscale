import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { TAG_KEY_MAX_SIZE } from "utils/constants";
import { getMaxLengthValidationDefinition } from "utils/validation";

const TAG_KEY = "tagKey";

const CreateClusterTypeFormTagKeyField = () => {
  const {
    register,
    formState: { errors }
  } = useFormContext();
  const intl = useIntl();

  return (
    <Input
      name={TAG_KEY}
      label={<FormattedMessage id={TAG_KEY} />}
      required
      error={!!errors[TAG_KEY]}
      helperText={errors[TAG_KEY] && errors[TAG_KEY].message}
      {...register(TAG_KEY, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: getMaxLengthValidationDefinition(TAG_KEY, TAG_KEY_MAX_SIZE)
      })}
      dataTestId="input_tag_key"
    />
  );
};

export default CreateClusterTypeFormTagKeyField;
