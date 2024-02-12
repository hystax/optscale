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
      /**
       *  Unregister the field to exclude it from the form state when
       *  booking for user other users (not for myself)
       */
      shouldUnregister
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

export default CreateSshKeyNameField;
