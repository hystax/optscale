import React from "react";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import RadioGroupField from "components/RadioGroupField";

export const FIELD_REASON = "reason";

export const REASONS = {
  SAVINGS: "savings",
  FEATURES: "features",
  GOAL: "goal",
  OTHER: "other"
};

export const getReasonValue = (reason) =>
  ({
    [REASONS.SAVINGS]: "The product does not give enough cost savings",
    [REASONS.FEATURES]: "OptScale does not work as expected / not enough features",
    [REASONS.GOAL]: "I have achieved my goal and am not interested in it anymore",
    [REASONS.OTHER]: "Other"
  }[reason]);

const ReasonsRadioGroup = () => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  return (
    <Controller
      control={control}
      name={FIELD_REASON}
      render={({ field }) => (
        <RadioGroupField
          fullWidth
          radioGroupProps={field}
          labelMessageId="reasonQuestion"
          error={errors?.[FIELD_REASON]}
          helperText={errors?.[FIELD_REASON]?.message}
          radioButtons={[
            {
              dataTestId: "radiobtn_savings",
              value: REASONS.SAVINGS,
              label: <FormattedMessage id="reasonSavings" />
            },
            {
              dataTestId: "radiobtn_features",
              value: REASONS.FEATURES,
              label: <FormattedMessage id="reasonFeatures" />
            },
            {
              dataTestId: "radiobtn_goal",
              value: REASONS.GOAL,
              label: <FormattedMessage id="reasonGoal" />
            },
            {
              dataTestId: "radiobtn_other",
              value: REASONS.OTHER,
              label: <FormattedMessage id="other" />
            }
          ]}
        />
      )}
    />
  );
};

export default ReasonsRadioGroup;
