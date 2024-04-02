import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getMlTaskRunUrl } from "urls";
import { formatRunFullName } from "utils/ml";

const run = ({ id, getRunNumber, getRunName, getRunId, getTaskId, headerMessageId, headerDataTestId }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  id,
  accessorFn: (rowOriginal) => {
    const runNumber = getRunNumber(rowOriginal);
    const runName = getRunName(rowOriginal);
    return formatRunFullName(runNumber, runName);
  },
  cell: ({ row: { original }, cell }) => {
    const runId = getRunId(original);
    const taskId = getTaskId(original);

    return (
      <Link to={getMlTaskRunUrl(taskId, runId)} component={RouterLink}>
        {cell.getValue()}
      </Link>
    );
  }
});

export default run;
