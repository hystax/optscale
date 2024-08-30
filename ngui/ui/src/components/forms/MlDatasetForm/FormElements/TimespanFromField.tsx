import { useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { DateTimePicker } from "components/forms/common/fields";
import { getNYearsFromToday } from "utils/datetime";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const FIELD_NAME = FIELD_NAMES.TIMESPAN_FROM;

const TimespanFromField = ({ isLoading = false }) => {
  const {
    formState: { isSubmitted },
    trigger
  } = useFormContext<FormValues>();

  const intl = useIntl();

  return (
    <DateTimePicker
      name={FIELD_NAME}
      labelMessageId="timespanFrom"
      notSetMessageId="timespanFrom"
      maxDate={getNYearsFromToday(1)}
      validate={{
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
      }}
      withTimePicker
      quickValues={{
        values: ["3h", "1d", "3d"],
        orValues: ["noLimit"]
      }}
      margin="dense"
      onChange={() => {
        if (isSubmitted) {
          trigger(FIELD_NAMES.TIMESPAN_TO);
        }
      }}
      isLoading={isLoading}
      fullWidth
    />
  );
};

export default TimespanFromField;
