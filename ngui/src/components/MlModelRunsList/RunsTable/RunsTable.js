import React, { useMemo } from "react";
import { Link } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useParams } from "react-router-dom";
import CollapsableTableCell from "components/CollapsableTableCell";
import FormattedMoney from "components/FormattedMoney";
import MlRunDuration from "components/MlRunDuration";
import MlRunStatus from "components/MlRunStatus/MlRunStatus";
import RunGoals from "components/RunGoals/RunGoals";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getMlModelRunUrl } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";
import { isEmpty as isEmptyObject } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";

const RunsTable = ({ runs, isLoading }) => {
  const { modelId: applicationId } = useParams();

  const columns = useMemo(
    () => [
      {
        header: <TextWithDataTestId dataTestId="lbl_#">#</TextWithDataTestId>,
        accessorKey: "number",
        defaultSort: "desc",
        cell: ({
          row: {
            original: { id, name, number }
          }
        }) => (
          <Link to={getMlModelRunUrl(applicationId, id)} component={RouterLink}>
            {`#${number}_${name}`}
          </Link>
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_status">
            <FormattedMessage id="status" />
          </TextWithDataTestId>
        ),
        accessorKey: "status",
        cell: ({ cell }) => <MlRunStatus status={cell.getValue()} />
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_started_at">
            <FormattedMessage id="startedAt" />
          </TextWithDataTestId>
        ),
        accessorKey: "start",
        cell: ({ cell }) => format(secondsToMilliseconds(cell.getValue()), EN_FULL_FORMAT)
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_duration">
            <FormattedMessage id="duration" />
          </TextWithDataTestId>
        ),
        accessorKey: "duration",
        cell: ({ cell }) => <MlRunDuration durationInSeconds={cell.getValue()} />
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_common_goals">
            <FormattedMessage id="goals" />
          </TextWithDataTestId>
        ),
        id: "goals",
        enableSorting: false,
        cell: ({
          row: {
            original: { goals, data: runData }
          }
        }) => {
          if (isEmptyArray(goals)) {
            return CELL_EMPTY_VALUE;
          }

          return <RunGoals goals={goals} runData={runData} />;
        }
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_expenses">
            <FormattedMessage id="expenses" />
          </TextWithDataTestId>
        ),
        accessorKey: "cost",
        cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_tags">
            <FormattedMessage id="tags" />
          </TextWithDataTestId>
        ),
        accessorKey: "tagsString",
        cell: ({
          row: {
            original: { tags = {} }
          }
        }) => (isEmptyObject(tags) ? CELL_EMPTY_VALUE : <CollapsableTableCell maxRows={5} tags={tags} />)
      }
    ],
    [applicationId]
  );

  // TODO ML: more sophisticated data patch for search purposes
  const tableData = useMemo(
    () =>
      runs.map((run) => ({
        ...run,
        duration: run.duration,
        tagsString: Object.entries(run.tags || {})
          .map(([key, val]) => `${key}: ${val}`)
          .join(" ")
      })),
    [runs]
  );

  return <Table withSearch isLoading={isLoading} data={tableData} columns={columns} />;
};

RunsTable.propTypes = {
  runs: PropTypes.array,
  isLoading: PropTypes.bool
};

export default RunsTable;
