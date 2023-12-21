import RangePickerForm from "components/RangePickerForm";
import { millisecondsToSeconds } from "utils/datetime";

export default {
  component: RangePickerForm
};

export const basic = () => (
  <RangePickerForm
    initialStartDateValue={millisecondsToSeconds(+new Date())}
    initialEndDateValue={millisecondsToSeconds(+new Date())}
    onApply={(startDateTimestamp, endDateTimestamp) => console.log("seconds timestamp:", startDateTimestamp, endDateTimestamp)}
  />
);
