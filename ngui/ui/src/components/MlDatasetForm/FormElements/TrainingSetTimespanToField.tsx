import React from "react";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import InputLoader from "components/InputLoader";
import IntervalTimePicker from "components/IntervalTimePicker";
import { getNYearsFromToday } from "utils/datetime";
import { FIELD_NAMES } from "../constants";

const TrainingSetTimespanToField = ({ name = FIELD_NAMES.TRAINING_SET_TIMESPAN_TO, isLoading = false }) => {
  const {
    formState: { errors, isSubmitted },
    control,
    trigger
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Controller
      name={name}
      control={control}
      rules={{
        validate: {
          lessThanOrEqualToTimespanTo: (timespanTo, formValues) => {
            const timespanFrom = formValues[FIELD_NAMES.TRAINING_SET_TIMESPAN_FROM];

            if (!timespanTo || !timespanFrom) {
              return true;
            }

            return timespanTo >= timespanFrom
              ? true
              : intl.formatMessage(
                  { id: "fieldMoreThanOrEqualToField" },
                  {
                    fieldName1: intl.formatMessage({ id: "timespanTo" }),
                    fieldName2: intl.formatMessage({ id: "timespanFrom" })
                  }
                );
          }
        }
      }}
      render={({ field: { value, onChange } }) => (
        <IntervalTimePicker
          value={value}
          labelMessageId="timespanTo"
          notSetMessageId="timespanTo"
          onApply={(date) => {
            onChange(+date);
            if (isSubmitted) {
              trigger(FIELD_NAMES.TRAINING_SET_TIMESPAN_FROM);
            }
          }}
          fullWidth
          margin="dense"
          maxDate={getNYearsFromToday(1)}
          validation={{
            dataTestId: `input_${name}`,
            error: !!errors[name],
            helperText: errors[name]?.message
          }}
          dataTestIds={{
            field: {
              input: `input_${name}`,
              iconButton: `btn_${name}select_date`
            }
          }}
        />
      )}
    />
  );
};

export default TrainingSetTimespanToField;
