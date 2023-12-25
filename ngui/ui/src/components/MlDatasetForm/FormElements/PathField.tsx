import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { FIELD_NAMES } from "../constants";

const IdField = ({ name = FIELD_NAMES.PATH, isLoading = false }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Input
      dataTestId="input_id"
      label={<FormattedMessage id="id" />}
      required
      autoFocus
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
            { inputName: intl.formatMessage({ id: "id" }), max: DEFAULT_MAX_INPUT_LENGTH }
          )
        }
      })}
    />
  );
};

export default IdField;
