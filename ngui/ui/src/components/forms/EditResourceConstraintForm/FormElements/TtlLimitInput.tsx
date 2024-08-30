import { useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { DateTimePicker } from "components/forms/common/fields";
import { isPast, INTERVAL_TTL_CONSTRAINT, startOfDay, getNYearsFromToday } from "utils/datetime";

const TtlLimitInput = ({ name, defaultValue }) => {
  const { trigger } = useFormContext();
  const intl = useIntl();

  return (
    <DateTimePicker
      name={name}
      defaultValue={defaultValue}
      notSetMessageId="notLimited"
      minDate={+startOfDay(new Date())}
      maxDate={getNYearsFromToday(5)}
      validate={{
        dateInPastValidation: (value) => {
          const isValidDate = value === 0 || value === undefined || !isPast(value);
          return isValidDate || intl.formatMessage({ id: "dateMustNotBeInThePast" });
        }
      }}
      margin="none"
      onChange={() => {
        trigger();
      }}
      quickValues={{
        values: ["3h", "1d", "3d"],
        orValues: ["noLimit"]
      }}
      intervalMinutes={INTERVAL_TTL_CONSTRAINT}
      withTimePicker
      fullWidth
    />
  );
};

export default TtlLimitInput;
