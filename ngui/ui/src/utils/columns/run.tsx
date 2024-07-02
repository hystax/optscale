import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getMlTaskRunUrl } from "urls";
import { formatRunFullName } from "utils/ml";

const run = ({
  id,
  getRunNumber,
  getRunName,
  getRunId,
  getTaskId,
  headerMessageId,
  headerDataTestId,
  enableSorting,
  runDetailsUrlOptions
}) => ({
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
  enableSorting,
  cell: ({ row: { original }, cell }) => {
    const runId = getRunId(original);
    const taskId = getTaskId(original);

    return (
      <Link to={getMlTaskRunUrl(taskId, runId, runDetailsUrlOptions)} component={RouterLink}>
        {cell.getValue()}
      </Link>
    );
  }
});

export default run;
