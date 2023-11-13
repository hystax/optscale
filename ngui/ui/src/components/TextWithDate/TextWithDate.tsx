import { formatRangeToShortNotation } from "utils/datetime";

// renders "short daterange format" surrounded by space and brackets: " (%DATERANGE%)"
const TextWithDate = ({ text, startDateTimestamp, endDateTimestamp }) => (
  <>
    {text}
    {startDateTimestamp && endDateTimestamp && <>&nbsp;({formatRangeToShortNotation(startDateTimestamp, endDateTimestamp)})</>}
  </>
);

export default TextWithDate;
