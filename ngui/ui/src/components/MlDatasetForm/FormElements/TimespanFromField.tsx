import { FormControl } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import InputLoader from "components/InputLoader";
import IntervalTimePicker from "components/IntervalTimePicker";
import { getNYearsFromToday } from "utils/datetime";
import { FIELD_NAMES } from "../constants";

const TimespanFromField = ({ name = FIELD_NAMES.TIMESPAN_FROM, isLoading = false }) => {
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
          lessThanOrEqualToTimespanTo: (timespanFrom, formValues) => {
            const timespanTo = formValues[FIELD_NAMES.TIMESPAN_TO];

            if (!timespanFrom || !timespanTo) {
              return true;
            }

            return timespanFrom <= timespanTo
              ? true
              : intl.formatMessage(
                  { id: "fieldLessThanOrEqualToField" },
                  {
                    fieldName1: intl.formatMessage({ id: "timespanFrom" }),
                    fieldName2: intl.formatMessage({ id: "timespanTo" })
                  }
                );
          }
        }
      }}
      render={({ field: { value, onChange } }) => (
        <FormControl fullWidth>
          <IntervalTimePicker
            value={value}
            labelMessageId="timespanFrom"
            notSetMessageId="timespanFrom"
            onApply={(date) => {
              onChange(+date);
              if (isSubmitted) {
                trigger(FIELD_NAMES.TIMESPAN_TO);
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
            withTimePicker
            dataTestIds={{
              field: {
                input: `input_${name}`,
                iconButton: `btn_${name}select_date`
              }
            }}
            quickValues={{
              values: ["3h", "1d", "3d"],
              orValues: ["noLimit"]
            }}
          />
        </FormControl>
      )}
    />
  );
};

export default TimespanFromField;
