import { useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { DateTimePicker } from "components/forms/common/fields";
import { getNYearsFromToday } from "utils/datetime";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const FIELD_NAME = FIELD_NAMES.TIMESPAN_TO;

const TimespanToField = ({ isLoading = false }) => {
  const {
    formState: { isSubmitted },
    trigger
  } = useFormContext<FormValues>();

  const intl = useIntl();

  return (
    <DateTimePicker
      name={FIELD_NAME}
      labelMessageId="timespanTo"
      notSetMessageId="timespanTo"
      maxDate={getNYearsFromToday(1)}
      validate={{
        lessThanOrEqualToTimespanTo: (timespanTo, formValues) => {
          const timespanFrom = formValues[FIELD_NAMES.TIMESPAN_FROM];

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
      }}
      withTimePicker
      quickValues={{
        values: ["3h", "1d", "3d"],
        orValues: ["noLimit"]
      }}
      margin="dense"
      onChange={() => {
        if (isSubmitted) {
          trigger(FIELD_NAMES.TIMESPAN_FROM);
        }
      }}
      isLoading={isLoading}
      fullWidth
    />
  );
};

export default TimespanToField;
