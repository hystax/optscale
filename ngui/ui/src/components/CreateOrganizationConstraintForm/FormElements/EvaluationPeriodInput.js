import React from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { positiveIntegerOrZero } from "utils/validation";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "../constants";

const FIELD_NAME = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.EVALUATION_PERIOD;

const EvaluationPeriodInput = () => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Input
      label={<FormattedMessage id="evaluationPeriod" />}
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
          value: 180,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: 180 })
        }
      })}
      InputProps={{
        endAdornment: intl.formatMessage({ id: "days" }).toLowerCase()
      }}
    />
  );
};

export default EvaluationPeriodInput;
