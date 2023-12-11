import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import IntervalTimePicker from "components/IntervalTimePicker";
import { isPast, INTERVAL_TTL_CONSTRAINT, startOfDay, getNYearsFromToday } from "utils/datetime";

const EditResourceConstraintFormTtlLimitInput = ({ name, defaultValue }) => {
  const {
    formState: { errors },
    control,
    trigger
  } = useFormContext();
  const intl = useIntl();

  return (
    <Controller
      name={name}
      defaultValue={defaultValue}
      control={control}
      rules={{
        validate: {
          dateInPastValidation: (value) => {
            const isValidDate = value === undefined || !isPast(value);
            return isValidDate || intl.formatMessage({ id: "dateMustNotBeInThePast" });
          }
        }
      }}
      render={({ field: { value, onChange } }) => (
        <IntervalTimePicker
          value={value}
          onApply={(date) => {
            onChange(date);
            trigger();
          }}
          fullWidth
          notSetMessageId="notLimited"
          minDate={+startOfDay(new Date())}
          maxDate={getNYearsFromToday(5)}
          validation={{
            error: !!errors[name],
            helperText: errors?.[name]?.message
          }}
          quickValues={{
            values: ["3h", "1d", "3d"],
            orValues: ["noLimit"]
          }}
          intervalMinutes={INTERVAL_TTL_CONSTRAINT}
          dataTestIds={{
            field: {
              input: "input_ttl",
              iconButton: "btn_select_date"
            },
            quickValues: {
              item: "btn_ttl"
            }
          }}
          withTimePicker
        />
      )}
    />
  );
};

export default EditResourceConstraintFormTtlLimitInput;
