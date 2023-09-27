import React from "react";
import { InputAdornment } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import QuestionMark from "components/QuestionMark";
import { MAX_INT_32 } from "utils/constants";
import { isPositiveNumberOrZero, notOnlyWhiteSpaces } from "utils/validation";

export const FIELD_NAME = "requiringAttention";

const RequiringAttentionInput = ({ isLoading }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <InputLoader margin="none" fullWidth />
  ) : (
    <Input
      dataTestId="input_requiring_attention"
      label={<FormattedMessage id="requiringAttention" />}
      required
      error={!!errors[FIELD_NAME]}
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="requiringAttentionDuplicatesSavingThresholdDescription"
            dataTestId="qmark_critical_duplicates_saving_threshold_description"
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
          positiveNumber: (value) => (isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "positiveNumberOrZero" }))
        }
      })}
    />
  );
};

export default RequiringAttentionInput;
