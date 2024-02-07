import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { NAME_MAX_SIZE } from "utils/constants";

const PoolFormNameInput = ({ isLoading, readOnly }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <InputLoader margin="normal" fullWidth />
  ) : (
    <Input
      label={<FormattedMessage id="name" />}
      required
      dataTestId="input_name"
      error={!!errors.name}
      helperText={errors.name && errors.name.message}
      InputProps={{
        readOnly
      }}
      {...register("name", {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: NAME_MAX_SIZE,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "value" }), max: NAME_MAX_SIZE }
          )
        }
      })}
    />
  );
};

export default PoolFormNameInput;
