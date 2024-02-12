import { useFormContext, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import Input from "components/Input";

export const KEY_VALUE_FIELD_ID = "key";

const CreateSshKeyValueField = () => {
  const intl = useIntl();

  const {
    control,
    formState: { errors }
  } = useFormContext();

  return (
    <Controller
      name={KEY_VALUE_FIELD_ID}
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
          error={!!errors[KEY_VALUE_FIELD_ID]}
          helperText={errors[KEY_VALUE_FIELD_ID] && errors[KEY_VALUE_FIELD_ID].message}
          label={intl.formatMessage({ id: "value" })}
          multiline
          rows={4}
          placeholder={intl.formatMessage({ id: "sshKeyPlaceholder" })}
          dataTestId="input_new_key_value"
          {...field}
        />
      )}
    />
  );
};

export default CreateSshKeyValueField;
