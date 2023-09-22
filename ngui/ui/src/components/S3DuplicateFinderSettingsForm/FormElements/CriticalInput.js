import React, { useEffect } from "react";
import { InputAdornment } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import QuestionMark from "components/QuestionMark";
import { MAX_INT_32 } from "utils/constants";
import { isPositiveNumberOrZero, notOnlyWhiteSpaces } from "utils/validation";
import { FIELD_NAME as REQUIRING_ATTENTION_FIELD_NAME } from "./RequiringAttentionInput";

export const FIELD_NAME = "critical";

const CriticalInput = ({ isLoading }) => {
  const {
    register,
    formState: { errors, isSubmitted },
    watch,
    trigger
  } = useFormContext();

  const intl = useIntl();

  const requiringAttention = watch(REQUIRING_ATTENTION_FIELD_NAME);

  useEffect(() => {
    if (isSubmitted) {
      trigger(FIELD_NAME);
    }
  }, [isSubmitted, requiringAttention, trigger]);

  return isLoading ? (
    <InputLoader margin="none" fullWidth />
  ) : (
    <Input
      dataTestId="input_critical"
      label={<FormattedMessage id="critical" />}
      required
      error={!!errors[FIELD_NAME]}
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="criticalDuplicatesSavingThresholdDescription"
            dataTestId="qmark_requiring_attention_duplicates_saving_threshold_description"
          />
        ),
        startAdornment: <InputAdornment position="start">$</InputAdornment>
      }}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      {...register(FIELD_NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        max: {
          value: MAX_INT_32,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
        },
        validate: {
          notOnlyWhiteSpaces,
          positiveNumber: (value) =>
            isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "positiveNumberOrZero" }),
          moreThanRequiringAttention: (value) =>
            requiringAttention.trim() === "" || value.trim() === "" || parseFloat(value) >= parseFloat(requiringAttention)
              ? true
              : intl.formatMessage(
                  { id: "fieldMoreThanOrEqualToField" },
                  {
                    fieldName1: intl.formatMessage({ id: "critical" }),
                    fieldName2: intl.formatMessage({ id: "requiringAttention" })
                  }
                )
        }
      })}
    />
  );
};

export default CriticalInput;
