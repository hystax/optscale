import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { MAX_INT_32 } from "utils/constants";
import { isPositiveNumberOrZero } from "utils/validation";

const TargetValueField = ({ name, isLoading }) => {
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
      label={<FormattedMessage id="targetValue" />}
      type="number"
      required
      error={!!errors[name]}
      helperText={errors[name] && errors[name].message}
      {...register(name, {
        valueAsNumber: true,
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        min: {
          value: 0,
          message: intl.formatMessage({ id: "moreOrEqual" }, { min: 0 })
        },
        max: {
          value: MAX_INT_32,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
        },
        validate: {
          positiveNumber: (value) => (isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "positiveNumber" }))
        }
      })}
      dataTestId="input_name"
    />
  );
};

export default TargetValueField;
