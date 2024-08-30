import { FormControl } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import InputLoader from "components/InputLoader";
import IntervalTimePicker from "components/IntervalTimePicker";

const DateTimePicker = ({
  name,
  labelMessageId,
  notSetMessageId,
  maxDate,
  minDate,
  validate,
  margin,
  onChange,
  quickValues,
  intervalMinutes,
  withTimePicker,
  defaultValue,
  required = false,
  isLoading = false,
  fullWidth = false
}) => {
  const {
    formState: { errors },
    control
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <InputLoader fullWidth={fullWidth} />
  ) : (
    <FormControl fullWidth={fullWidth} margin={margin}>
      <Controller
        name={name}
        control={control}
        defaultValue={defaultValue}
        rules={{
          required: {
            value: required,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          validate
        }}
        render={({ field: { value, onChange: fieldOnChange } }) => (
          <IntervalTimePicker
            value={value}
            labelMessageId={labelMessageId}
            notSetMessageId={notSetMessageId}
            required={required}
            onApply={(date) => {
              fieldOnChange(+date);

              if (typeof onChange === "function") {
                onChange(+date);
              }
            }}
            fullWidth={fullWidth}
            margin="none"
            minDate={minDate}
            maxDate={maxDate}
            validation={{
              dataTestId: `input_${name}`,
              error: !!errors[name],
              helperText: errors[name]?.message
            }}
            dataTestIds={{
              field: {
                input: `input_${name}`,
                iconButton: `btn_${name}_select_date`
              },
              quickValues: {
                item: `btn_quick_value_${name}`
              }
            }}
            quickValues={quickValues}
            intervalMinutes={intervalMinutes}
            withTimePicker={withTimePicker}
          />
        )}
      />
    </FormControl>
  );
};

export default DateTimePicker;
