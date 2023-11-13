import RangePickerForm from "components/RangePickerForm";
import { KINDS } from "stories";
import { millisecondsToSeconds } from "utils/datetime";

export default {
  title: `${KINDS.FORMS}/RangePickerForm`
};

export const basic = () => (
  <RangePickerForm
    initialStartDateValue={millisecondsToSeconds(+new Date())}
    initialEndDateValue={millisecondsToSeconds(+new Date())}
    onApply={(startDateTimestamp, endDateTimestamp) => console.log("seconds timestamp:", startDateTimestamp, endDateTimestamp)}
  />
);
