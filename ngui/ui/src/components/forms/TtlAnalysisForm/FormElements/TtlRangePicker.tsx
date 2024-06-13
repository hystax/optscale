import { useEffect } from "react";
import { useFormContext } from "react-hook-form";
import RangePicker from "components/RangePicker";
import { useRangePickerValidationRules } from "hooks/useRangePickerValidationRules";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const startDatePickerName = FIELD_NAMES.START_DATE_PICKER_NAME;
const endDatePickerName = FIELD_NAMES.END_DATE_PICKER_NAME;

const TtlRangePicker = ({ formValuesGetter }) => {
  const { startDateValidationRules, endDateValidationRules } = useRangePickerValidationRules({
    startDatePickerName,
    endDatePickerName,
    formValuesGetter
  });

  const {
    register,
    setValue,
    clearErrors,
    watch,
    formState: { errors }
  } = useFormContext<FormValues>();

  const [watchStartDate, watchEndDate] = watch([startDatePickerName, endDatePickerName]);

  useEffect(() => {
    register(startDatePickerName, {
      validate: startDateValidationRules
    });
    register(endDatePickerName, {
      validate: endDateValidationRules
    });
  }, [register, startDateValidationRules, endDateValidationRules]);

  return (
    <RangePicker
      initialDateRange={{ startDate: watchStartDate, endDate: watchEndDate }}
      validation={{
        error: !!errors[startDatePickerName] || !!errors[endDatePickerName],
        helperText: errors?.[startDatePickerName]?.message || errors?.[endDatePickerName]?.message
      }}
      onChange={(dateRange) => {
        setValue(startDatePickerName, dateRange.startDate);
        setValue(endDatePickerName, dateRange.endDate);
        clearErrors([startDatePickerName, endDatePickerName]);
      }}
    />
  );
};

export default TtlRangePicker;
