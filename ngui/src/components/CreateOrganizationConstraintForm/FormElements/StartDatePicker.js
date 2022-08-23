import React from "react";
import { Controller, useFormContext } from "react-hook-form";
import IntervalTimePicker from "components/IntervalTimePicker";
import { INTERVAL_TTL_CONSTRAINT, subDays, getNYearsFromToday } from "utils/datetime";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "../constants";

const FIELD_NAME = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.START_DATE;

const StartDatePicker = () => {
  const {
    formState: { errors },
    control,
    trigger
  } = useFormContext();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      render={({ field: { value, onChange } }) => (
        <IntervalTimePicker
          labelMessageId="startDate"
          value={+value}
          onApply={(date) => {
            onChange(date);
            trigger();
          }}
          fullWidth
          margin="dense"
          minDate={+subDays(new Date(), 180)}
          maxDate={getNYearsFromToday(1)}
          validation={{
            dataTestId: `input_${FIELD_NAME}`,
            error: !!errors[FIELD_NAME],
            helperText: errors[FIELD_NAME]?.message
          }}
          intervalMinutes={INTERVAL_TTL_CONSTRAINT}
          dataTestIds={{
            field: {
              input: `input_${FIELD_NAME}`,
              iconButton: "btn_select_date"
            }
          }}
        />
      )}
    />
  );
};

export default StartDatePicker;
