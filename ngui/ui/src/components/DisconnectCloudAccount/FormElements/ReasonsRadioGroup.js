import React from "react";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import RadioGroupField from "components/RadioGroupField";

export const FIELD_REASON = "reason";
export const VALUE_OTHER = "other";

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
              value: "savings",
              label: <FormattedMessage id="reasonSavings" />
            },
            {
              dataTestId: "radiobtn_features",
              value: "features",
              label: <FormattedMessage id="reasonFeatures" />
            },
            {
              dataTestId: "radiobtn_goal",
              value: "goal",
              label: <FormattedMessage id="reasonGoal" />
            },
            {
              dataTestId: "radiobtn_other",
              value: VALUE_OTHER,
              label: <FormattedMessage id="other" />
            }
          ]}
        />
      )}
    />
  );
};

export default ReasonsRadioGroup;
