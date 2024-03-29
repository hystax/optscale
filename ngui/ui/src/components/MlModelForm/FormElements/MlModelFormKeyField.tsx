import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

export const FIELD_NAME = "key";

const MlModelFormKeyField = ({ name = FIELD_NAME, isLoading = false }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Input
      dataTestId="input_name"
      label={<FormattedMessage id="key" />}
      required
      error={!!errors[name]}
      helperText={errors[name] && errors[name].message}
      {...register(name, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "key" }), max: DEFAULT_MAX_INPUT_LENGTH }
          )
        }
      })}
    />
  );
};

export default MlModelFormKeyField;
