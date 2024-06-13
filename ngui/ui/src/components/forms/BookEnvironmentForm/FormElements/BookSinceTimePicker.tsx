import { useFormContext } from "react-hook-form";
import { DateTimePicker } from "components/forms/common/fields";
import { startOfDay, roundTimeToInterval, INTERVAL_ENVIRONMENT, getNYearsFromToday } from "utils/datetime";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.BOOK_SINCE;

const BookSinceTimePicker = ({ validate }) => {
  const { trigger } = useFormContext();

  const today = roundTimeToInterval(+new Date(), INTERVAL_ENVIRONMENT);

  return (
    <DateTimePicker
      name={FIELD_NAME}
      labelMessageId="bookSince"
      notSetMessageId="now"
      minDate={+startOfDay(today)} // get start of a day to be able to select it in a calendar
      maxDate={getNYearsFromToday(5)}
      validate={validate}
      onChange={() => {
        trigger();
      }}
      fullWidth
      quickValues={{
        values: ["now", "3h", "1d", "3d"]
      }}
      intervalMinutes={INTERVAL_ENVIRONMENT}
      withTimePicker
    />
  );
};

export default BookSinceTimePicker;
