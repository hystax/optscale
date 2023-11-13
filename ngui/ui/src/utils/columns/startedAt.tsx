import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";

const startedAt = ({ headerMessageId, headerDataTestId, accessorKey, options = {} }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => format(secondsToMilliseconds(cell.getValue()), EN_FULL_FORMAT),
  ...options
});

export default startedAt;
