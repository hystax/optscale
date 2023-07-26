import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useFormContext } from "react-hook-form";
import RangePicker from "components/RangePicker";
import { useRangePickerValidationRules } from "hooks/useRangePickerValidationRules";

const TtlAnalysisFormRangePicker = ({ startDatePickerName, endDatePickerName, formValuesGetter }) => {
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
  } = useFormContext();

  const [watchStartDate, watchEndDate] = watch([startDatePickerName, endDatePickerName]);

  useEffect(() => {
    register(startDatePickerName, {
      validate: startDateValidationRules
    });
    register(endDatePickerName, {
      validate: endDateValidationRules
    });
  }, [register, startDatePickerName, startDateValidationRules, endDatePickerName, endDateValidationRules]);

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

TtlAnalysisFormRangePicker.propTypes = {
  startDatePickerName: PropTypes.string.isRequired,
  endDatePickerName: PropTypes.string.isRequired,
  formValuesGetter: PropTypes.func.isRequired
};

export default TtlAnalysisFormRangePicker;
