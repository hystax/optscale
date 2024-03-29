import { useMemo } from "react";
import { Typography } from "@mui/material";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import CircleLabel from "components/CircleLabel";
import SubTitle from "components/SubTitle";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getMlTaskDetailsUrl, getMlRunsetDetailsUrl } from "urls";
import { duration, expenses, startedAt, text } from "utils/columns";
import { ML_RUN_STATUS } from "utils/constants";
import { formatRunFullName } from "utils/ml";

const RunsetNameCell = ({
  cell,
  row: {
    original: { id, state }
  }
}) => (
  <CaptionedCell
    caption={
      state === ML_RUN_STATUS.RUNNING
        ? {
            key: `running`,
            node: (
              <CircleLabel
                figureColor="success"
                label={
                  <Typography variant="caption">
                    <FormattedMessage id="running" />
                  </Typography>
                }
                textFirst={false}
              />
            )
          }
        : undefined
    }
  >
    <Link to={getMlRunsetDetailsUrl(id)} component={RouterLink}>
      {cell.getValue()}
    </Link>
  </CaptionedCell>
);

const RunsetsTable = ({ runsets, isLoading }) => {
  const columns = useMemo(
    () => [
      {
        header: <TextWithDataTestId dataTestId="lbl_#">#</TextWithDataTestId>,
        id: "number",
        accessorFn: ({ number, name }) => formatRunFullName(number, name),
        defaultSort: "desc",
        sortingFn: "alphanumeric",
        cell: ({ cell, row }) => <RunsetNameCell cell={cell} row={row} />
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_task">
            <FormattedMessage id="task" />
          </TextWithDataTestId>
        ),
        id: "task",
        accessorFn: ({ task = {} }) => task.name,
        cell: ({
          cell,
          row: {
            original: { task }
          }
        }) => {
          const { id, deleted } = task;

          return deleted ? (
            cell.getValue()
          ) : (
            <Link to={getMlTaskDetailsUrl(id)} component={RouterLink}>
              {cell.getValue()}
            </Link>
          );
        }
      },
      startedAt({
        headerMessageId: "startedAt",
        headerDataTestId: "lbl_started_at",
        accessorKey: "created_at",
        options: {
          enableGlobalFilter: false
        }
      }),
      text({
        id: "started_by",
        accessorFn: ({ owner }) => owner?.name,
        headerMessageId: "startedBy",
        headerDataTestId: "lbl_started_by",
        accessorKey: "started_by"
      }),
      duration({
        headerMessageId: "duration",
        headerDataTestId: "lbl_duration",
        accessorKey: "duration"
      }),
      text({
        headerMessageId: "configurationsTried",
        headerDataTestId: "lbl_configurations_tried",
        accessorKey: "runs_count"
      }),
      text({
        headerMessageId: "completedRuns",
        headerDataTestId: "lbl_completed_runs",
        accessorKey: "succeeded_runs"
      }),
      expenses({
        headerDataTestId: "lbl_expenses",
        headerMessageId: "expenses",
        accessorKey: "cost"
      })
    ],
    []
  );

  const data = useMemo(() => runsets, [runsets]);

  return (
    <>
      <SubTitle>
        <FormattedMessage id="runsets" />
      </SubTitle>
      {isLoading ? (
        <TableLoader columnsCounter={4} />
      ) : (
        <Table
          columns={columns}
          data={data}
          pageSize={50}
          localization={{
            emptyMessageId: "noRunsets"
          }}
        />
      )}
    </>
  );
};

export default RunsetsTable;
