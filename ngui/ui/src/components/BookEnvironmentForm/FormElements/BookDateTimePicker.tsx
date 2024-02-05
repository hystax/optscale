import { Controller, useFormContext } from "react-hook-form";
import IntervalTimePicker from "components/IntervalTimePicker";
import { startOfDay, roundTimeToInterval, AMOUNT_30_MINUTES } from "utils/datetime";

const BookDateTimePicker = ({
  name,
  maxDate,
  required,
  rules = {},
  quickValues,
  intervalMinutes = AMOUNT_30_MINUTES,
  notSetMessageId = "notLimited"
}) => {
  const {
    control,
    formState: { errors },
    trigger
  } = useFormContext();

  const today = roundTimeToInterval(+new Date(), intervalMinutes);

  return (
    <Controller
      name={name}
      control={control}
      rules={rules}
      render={({ field: { value, onChange } }) => (
        <IntervalTimePicker
          value={value}
          onApply={(date) => {
            onChange(date);
            trigger();
          }}
          labelMessageId={name}
          fullWidth
          notSetMessageId={notSetMessageId}
          // TODO: maxDate and minDate are number and date respectively, cast to one type
          minDate={+startOfDay(today)} // get start of a day to be able to select it in a calendar
          maxDate={maxDate}
          required={required}
          validation={{
            error: !!errors[name],
            helperText: errors?.[name]?.message
          }}
          quickValues={quickValues}
          intervalMinutes={intervalMinutes}
          withTimePicker
        />
      )}
    />
  );
};

export default BookDateTimePicker;
