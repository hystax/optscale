import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const mlRunsCount = ({ headerDataTestId = "lbl_runs_count", accessorKey = "runs_count" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="runsCount" />
    </TextWithDataTestId>
  ),
  accessorKey
});

export default mlRunsCount;
