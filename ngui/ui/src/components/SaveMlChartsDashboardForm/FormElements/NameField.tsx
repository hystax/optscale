import { useFormContext } from "react-hook-form";
import { useIntl, FormattedMessage } from "react-intl";
import Input from "components/Input";
import { notOnlyWhiteSpaces } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const NAME_MAX_SIZE = 30;

const NameField = ({ name = FIELD_NAMES.NAME, disabled = false }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Input
      label={<FormattedMessage id="name" />}
      required
      autoFocus
      dataTestId="input_name"
      disabled={disabled}
      error={!!errors[name]}
      helperText={errors[name] && errors[name].message}
      {...register(name, {
        required: {
          value: !disabled,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: NAME_MAX_SIZE,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "value" }), max: NAME_MAX_SIZE }
          )
        },
        validate: { notOnlyWhiteSpaces }
      })}
    />
  );
};

export default NameField;
