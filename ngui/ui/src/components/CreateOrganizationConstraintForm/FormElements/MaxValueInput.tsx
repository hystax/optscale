import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { MAX_INT_32 } from "utils/constants";
import { positiveInteger } from "utils/validation";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "../constants";

const FIELD_NAME = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.MAX_VALUE;

const MaxValueInput = () => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Input
      label={<FormattedMessage id="quotaPolicyMaxValue" />}
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
          positiveInteger
        },
        max: {
          value: MAX_INT_32,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
        }
      })}
    />
  );
};

export default MaxValueInput;
