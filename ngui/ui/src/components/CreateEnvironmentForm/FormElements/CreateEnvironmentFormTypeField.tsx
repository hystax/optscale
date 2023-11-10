import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { TAG_KEY_MAX_SIZE } from "utils/constants";
import { getMaxLengthValidationDefinition } from "utils/validation";

const RESOURCE_TYPE = "resourceType";

const CreateEnvironmentFormTypeField = () => {
  const {
    register,
    formState: { errors }
  } = useFormContext();
  const intl = useIntl();

  return (
    <Input
      name={RESOURCE_TYPE}
      label={<FormattedMessage id={RESOURCE_TYPE} />}
      required
      error={!!errors[RESOURCE_TYPE]}
      helperText={errors[RESOURCE_TYPE] && errors[RESOURCE_TYPE].message}
      {...register(RESOURCE_TYPE, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: getMaxLengthValidationDefinition(RESOURCE_TYPE, TAG_KEY_MAX_SIZE)
      })}
      dataTestId="input_tag_key"
    />
  );
};

export default CreateEnvironmentFormTypeField;
