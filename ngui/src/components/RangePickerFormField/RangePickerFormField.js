import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import RangePicker from "components/RangePicker";
import { isAfter, isValid, getMinPickerDateSec, getMaxPickerDateSec, secondsToMilliseconds } from "utils/datetime";

const RangePickerFormField = ({
  startDatePickerName,
  endDatePickerName,
  defaultStartDate,
  defaultEndDate,
  onStartDateChange,
  onEndDateChange,
  notSetMessageId,
  isUtc = true
}) => {
  const intl = useIntl();

  const {
    register,
    setValue,
    getValues,
    clearErrors,
    unregister,
    watch,
    formState: { errors }
  } = useFormContext();

  useEffect(() => {
    register(startDatePickerName, {
      validate: {
        valid: (value) =>
          value && !isValid(secondsToMilliseconds(value)) ? intl.formatMessage({ id: "invalidDateFormat" }) : true,
        minDate: (value) =>
          isAfter(getMinPickerDateSec(isUtc), value)
            ? intl.formatMessage({ id: "startDateShouldBeGreaterThanOrEqualToFirstJan2000" })
            : true,
        isLessThanEndDate: (value) => {
          const { [endDatePickerName]: endDate } = getValues();
          const valueMS = secondsToMilliseconds(value);
          const endDateMS = secondsToMilliseconds(endDate);
          if (isAfter(valueMS, endDateMS)) {
            return intl.formatMessage({ id: "startDateShouldNotBeGreaterThanEndTime" });
          }
          // We can't use cached value for the max picker date value because in some cases
          // validation may fail for the valid date
          // (for more info see: https://datatrendstech.atlassian.net/browse/NGUI-915)
          if (isAfter(value, getMaxPickerDateSec(isUtc))) {
            return intl.formatMessage({ id: "startDateShouldNotBeInTheFuture" });
          }
          return true;
        }
      }
    });
    register(endDatePickerName, {
      validate: {
        valid: (value) =>
          value && !isValid(secondsToMilliseconds(value)) ? intl.formatMessage({ id: "invalidDateFormat" }) : true,
        maxDate: (value) =>
          // We can't use cached value for the max picker date value because in some cases
          // validation may fail for the valid date
          // (for more info see: https://datatrendstech.atlassian.net/browse/NGUI-915)
          isAfter(value, getMaxPickerDateSec(isUtc)) ? intl.formatMessage({ id: "endDateShouldNotBeInTheFuture" }) : true,
        isGreaterThanStartDate: (value) => {
          const { [startDatePickerName]: startDate } = getValues();
          return isAfter(secondsToMilliseconds(startDate), secondsToMilliseconds(value))
            ? intl.formatMessage({ id: "endDateShouldBeGreaterThanStartTime" })
            : true;
        }
      }
    });
    return () => {
      unregister(startDatePickerName);
      unregister(endDatePickerName);
    };
  }, [clearErrors, endDatePickerName, getValues, intl, register, startDatePickerName, unregister, isUtc]);

  useEffect(() => {
    if (defaultStartDate) {
      setValue(startDatePickerName, defaultStartDate);
    }
    if (defaultEndDate) {
      setValue(endDatePickerName, defaultEndDate);
    }
  }, [defaultEndDate, defaultStartDate, endDatePickerName, setValue, startDatePickerName]);

  const { [startDatePickerName]: startDateTime, [endDatePickerName]: endDateTime } = watch();

  return (
    <RangePicker
      initialDateRange={{ startDate: startDateTime, endDate: endDateTime }}
      validation={{
        error: !!errors[startDatePickerName] || !!errors[endDatePickerName],
        helperText: errors?.[startDatePickerName]?.message || errors?.[endDatePickerName]?.message
      }}
      onChange={(dateRange) => {
        setValue(startDatePickerName, dateRange.startDate);
        setValue(endDatePickerName, dateRange.endDate);

        clearErrors([startDatePickerName, endDatePickerName]);

        if (typeof onStartDateChange === "function") {
          onStartDateChange(dateRange.startDate);
        }
        if (typeof onEndDateChange === "function") {
          onEndDateChange(dateRange.endDate);
        }
      }}
      notSetMessageId={notSetMessageId}
      fullWidth
      isUtc={isUtc}
    />
  );
};

RangePickerFormField.propTypes = {
  startDatePickerName: PropTypes.string.isRequired,
  endDatePickerName: PropTypes.string.isRequired,
  defaultStartDate: PropTypes.number,
  defaultEndDate: PropTypes.number,
  onStartDateChange: PropTypes.func,
  onEndDateChange: PropTypes.func,
  notSetMessageId: PropTypes.string,
  isUtc: PropTypes.bool
};

export default RangePickerFormField;
