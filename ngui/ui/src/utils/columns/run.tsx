import { Link, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getMlTaskDetailsUrl, getMlTaskRunUrl } from "urls";
import { formatRunFullName } from "utils/ml";

const run = ({
  id,
  getRunNumber,
  getRunName,
  getRunId,
  getTaskId,
  getTaskName,
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
    const taskName = getTaskName?.(original);

    const runLink = (
      <Link to={getMlTaskRunUrl(taskId, runId, runDetailsUrlOptions)} component={RouterLink}>
        {cell.getValue()}
      </Link>
    );

    if (taskName) {
      return (
        <CaptionedCell
          caption={{
            node: (
              <Typography variant="caption">
                <Link to={getMlTaskDetailsUrl(taskId)} component={RouterLink}>
                  {taskName}
                </Link>
              </Typography>
            )
          }}
        >
          {runLink}
        </CaptionedCell>
      );
    }

    return runLink;
  }
});

export default run;
