import { FormattedMessage } from "react-intl";
import TextWithDate from "components/TextWithDate";

const ExpensesTableHeader = ({ startDateTimestamp, endDateTimestamp }) => (
  <TextWithDate
    text={<FormattedMessage id="expenses" />}
    startDateTimestamp={startDateTimestamp}
    endDateTimestamp={endDateTimestamp}
  />
);

export default ExpensesTableHeader;
