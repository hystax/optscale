import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";

const datasetTimespan = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_timespan">
      <FormattedMessage id="timespan" />
    </TextWithDataTestId>
  ),
  id: "timespan",
  cell: ({
    row: {
      original: { timespan_from: timespanFrom, timespan_to: timespanTo }
    }
  }) => (
    <>
      <KeyValueLabel
        keyMessageId="from"
        value={timespanFrom ? format(secondsToMilliseconds(timespanFrom), EN_FULL_FORMAT) : undefined}
      />
      <KeyValueLabel
        keyMessageId="to"
        value={timespanTo ? format(secondsToMilliseconds(timespanTo), EN_FULL_FORMAT) : undefined}
      />
    </>
  )
});

export default datasetTimespan;
