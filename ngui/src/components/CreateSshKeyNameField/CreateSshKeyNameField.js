import React from "react";
import { useFormContext, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import Input from "components/Input";

export const KEY_NAME_FIELD_ID = "name";

const CreateSshKeyNameField = () => {
  const intl = useIntl();

  const {
    control,
    formState: { errors }
  } = useFormContext();

  return (
    <Controller
      name={KEY_NAME_FIELD_ID}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      defaultValue=""
      render={({ field }) => (
        <Input
          required
          error={!!errors[KEY_NAME_FIELD_ID]}
          helperText={errors[KEY_NAME_FIELD_ID] && errors[KEY_NAME_FIELD_ID].message}
          label={intl.formatMessage({ id: "name" })}
          placeholder={intl.formatMessage({ id: "sshNamePlaceholder" })}
          dataTestId="input_new_key_title"
          {...field}
        />
      )}
    />
  );
};

CreateSshKeyNameField.propTypes = {};

export default CreateSshKeyNameField;
