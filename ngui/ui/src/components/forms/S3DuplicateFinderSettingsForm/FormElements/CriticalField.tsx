import { useEffect } from "react";
import { InputAdornment } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { isPositiveNumberOrZero } from "utils/validation";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const FIELD_NAME = FIELD_NAMES.CRITICAL;

const CriticalField = ({ isLoading = false }) => {
  const {
    formState: { isSubmitted },
    watch,
    trigger
  } = useFormContext<FormValues>();

  const intl = useIntl();

  const requiringAttention = watch(FIELD_NAMES.REQUIRING_ATTENTION);

  useEffect(() => {
    if (isSubmitted) {
      trigger(FIELD_NAME);
    }
  }, [isSubmitted, requiringAttention, trigger]);

  return (
    <NumberInput
      name={FIELD_NAME}
      label={<FormattedMessage id="critical" />}
      required
      dataTestId="input_critical"
      isLoading={isLoading}
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="criticalDuplicatesSavingThresholdDescription"
            dataTestId="qmark_requiring_attention_duplicates_saving_threshold_description"
          />
        ),
        startAdornment: <InputAdornment position="start">$</InputAdornment>
      }}
      validate={{
        positiveNumber: (value) => (isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "positiveNumberOrZero" })),
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
      }}
    />
  );
};

export default CriticalField;
