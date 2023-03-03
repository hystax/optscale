import React from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { NAME_MAX_SIZE } from "utils/constants";
import { getMaxLengthValidationDefinition } from "utils/validation";

const FIELD_MESSAGE_ID = "name";

const MlApplicationParameterFormNameField = ({ name, isLoading }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();
  const intl = useIntl();

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Input
      name={name}
      label={<FormattedMessage id={FIELD_MESSAGE_ID} />}
      required
      error={!!errors[name]}
      helperText={errors[name] && errors[name].message}
      {...register(name, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: getMaxLengthValidationDefinition(FIELD_MESSAGE_ID, NAME_MAX_SIZE)
      })}
      dataTestId="input_name"
    />
  );
};

export default MlApplicationParameterFormNameField;
