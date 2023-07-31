import React from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { NAME_MAX_SIZE } from "utils/constants";
import { getMaxLengthValidationDefinition } from "utils/validation";

const NAME = "name";

const CreateEnvironmentFormNameField = () => {
  const {
    register,
    formState: { errors }
  } = useFormContext();
  const intl = useIntl();

  return (
    <Input
      name={NAME}
      label={<FormattedMessage id={NAME} />}
      required
      error={!!errors[NAME]}
      helperText={errors[NAME] && errors[NAME].message}
      {...register(NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: getMaxLengthValidationDefinition(NAME, NAME_MAX_SIZE)
      })}
      dataTestId="input_name"
    />
  );
};

export default CreateEnvironmentFormNameField;
