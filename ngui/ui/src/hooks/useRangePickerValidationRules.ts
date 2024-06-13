import { useMemo } from "react";
import { useIntl } from "react-intl";
import { START_DATE_PICKER_NAME, END_DATE_PICKER_NAME } from "utils/constants";
import {
  isEqual,
  startOfDay,
  isAfter,
  isValid,
  secondsToMilliseconds,
  getMaxPickerDateSec,
  getMinPickerDateSec,
  performDateTimeFunction
} from "utils/datetime";

export const useRangePickerValidationRules = ({
  startDatePickerName = START_DATE_PICKER_NAME,
  endDatePickerName = END_DATE_PICKER_NAME,
  formValuesGetter,
  isUtc = true
}) => {
  const intl = useIntl();

  // TODO: both validation rules looks really close — could be generalized. Also we could use them inside RangePickerFormField.js validation somehow

  // Memoization is used to prevent firing custom registers on each update in
  // useEffect that includes these validation rules in the dependency array
  // see TtlAnalysisFormRangePicker
  const startDateValidationRules = useMemo(
    () => ({
      required: (value) => (!value ? intl.formatMessage({ id: "thisFieldIsRequired" }) : true),
      valid: (value) => (!isValid(secondsToMilliseconds(value)) ? intl.formatMessage({ id: "invalidDateFormat" }) : true),
      minDate: (value) =>
        isAfter(getMinPickerDateSec(isUtc), value)
          ? intl.formatMessage({ id: "startDateMustBeGreaterThanOrEqualToFirstJan2000" })
          : true,
      isLessThanEndDate: (value) => {
        const { [endDatePickerName]: end } = formValuesGetter();
        const valueMS = secondsToMilliseconds(value);
        const endMS = secondsToMilliseconds(end);
        const isSameDay = isEqual(
          performDateTimeFunction(startOfDay, isUtc, valueMS),
          performDateTimeFunction(startOfDay, isUtc, endMS)
        );
        if (!isSameDay && isAfter(valueMS, endMS)) {
          return intl.formatMessage({ id: "startDateMustNotBeGreaterThanEndTime" });
        }
        // We can't use cached value for the max picker date value because in some cases
        // validation may fail for the valid date
        // (for more info see: https://datatrendstech.atlassian.net/browse/NGUI-915)
        if (isAfter(value, getMaxPickerDateSec(isUtc))) {
          return intl.formatMessage({ id: "startDateMustNotBeInTheFuture" });
        }
        return true;
      }
    }),
    [endDatePickerName, formValuesGetter, intl, isUtc]
  );

  const endDateValidationRules = useMemo(
    () => ({
      required: (value) => (!value ? intl.formatMessage({ id: "thisFieldIsRequired" }) : true),
      valid: (value) => (!isValid(secondsToMilliseconds(value)) ? intl.formatMessage({ id: "invalidDateFormat" }) : true),
      maxDate: (value) =>
        // We can't use cached value for the max picker date value because in some cases
        // validation may fail for the valid date
        // (for more info see: https://datatrendstech.atlassian.net/browse/NGUI-915)
        isAfter(value, getMaxPickerDateSec(isUtc)) ? intl.formatMessage({ id: "endDateMustNotBeInTheFuture" }) : true,
      isGreaterThanStartDate: (value) => {
        const { [startDatePickerName]: start } = formValuesGetter();
        const valueMS = secondsToMilliseconds(value);
        const startMS = secondsToMilliseconds(start);
        const isSameDay = isEqual(
          performDateTimeFunction(startOfDay, isUtc, valueMS),
          performDateTimeFunction(startOfDay, isUtc, startMS)
        );
        if (!isSameDay && isAfter(startMS, valueMS)) {
          return intl.formatMessage({ id: "endDateMustBeGreaterThanStartTime" });
        }
        return true;
      }
    }),
    [formValuesGetter, intl, startDatePickerName, isUtc]
  );

  return {
    startDateValidationRules,
    endDateValidationRules
  };
};
