import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { positiveIntegerOrZero } from "utils/validation";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "../constants";

const FIELD_NAME = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.THRESHOLD;

const ThresholdInput = () => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Input
      label={<FormattedMessage id="threshold" />}
      required
      dataTestId={`input_${FIELD_NAME}`}
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME]?.message}
      {...register(FIELD_NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        validate: {
          positiveIntegerOrZero
        },
        max: {
          value: 1000,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: 1000 })
        }
      })}
      InputProps={{
        endAdornment: "%"
      }}
    />
  );
};

export default ThresholdInput;
