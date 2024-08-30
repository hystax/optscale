import { useMemo, useState, Fragment } from "react";
import { Link } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CircleLabel from "components/CircleLabel";
import ExecutorLabel from "components/ExecutorLabel";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import MlRunStatusCell from "components/MlRunStatusCell";
import MlRunStatusHeaderCell from "components/MlRunStatusHeaderCell";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsOptScaleModeEnabled } from "hooks/useIsOptScaleModeEnabled";
import { getMlTaskRunUrl } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { duration, startedAt, dataset, hyperparameters, metrics } from "utils/columns";
import { OPTSCALE_MODE } from "utils/constants";
import { formatRunFullName, getFirstMetricEntryKey, getRunsReachedGoalsKeyNameEntries } from "utils/ml";
import { isEmpty as isEmptyObject } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";

const ExecutorsCellContent = ({ executors }) => {
  const isFinOpsEnabled = useIsOptScaleModeEnabled(OPTSCALE_MODE.FINOPS);

  return isEmptyArray(executors) ? (
    CELL_EMPTY_VALUE
  ) : (
    <div>
      {executors.map(
        ({ instance_id: instanceId, platform_type: platformType, instance_type: instanceType, total_cost: cost }) => (
          <Fragment key={instanceId}>
            <ExecutorLabel instanceId={instanceId} platformType={platformType} />
            {instanceType && <KeyValueLabel keyMessageId="size" value={instanceType} />}
            {isFinOpsEnabled && cost ? <KeyValueLabel keyMessageId="expenses" value={<FormattedMoney value={cost} />} /> : null}
          </Fragment>
        )
      )}
    </div>
  );
};

const RunsTable = ({ runs, isLoading = false }) => {
  const theme = useTheme();

  const metricsKeyNameEntries = getRunsReachedGoalsKeyNameEntries(runs);

  const [sortByMetricKey, setSortByMetricKey] = useState(getFirstMetricEntryKey(metricsKeyNameEntries));

  const columns = useMemo(
    () => [
      {
        header: <TextWithDataTestId dataTestId="lbl_#">#</TextWithDataTestId>,
        id: "runNumber",
        accessorFn: ({ number, name }) => formatRunFullName(number, name),
        defaultSort: "desc",
        sortingFn: "alphanumeric",
        cell: ({
          cell,
          row: {
            original: { id, color, task_id: taskId }
          }
        }) => (
          <CircleLabel
            figureColor={color}
            textFirst={false}
            label={
              <Link to={getMlTaskRunUrl(taskId, id)} component={RouterLink}>
                {cell.getValue()}
              </Link>
            }
          />
        )
      },
      {
        header: <MlRunStatusHeaderCell />,
        accessorKey: "status",
        cell: ({
          row: {
            original: { reason, status }
          }
        }) => <MlRunStatusCell reason={reason} status={status} />
      },
      metrics({
        accessorKey: "reached_goals",
        onSortByMetricKeyChange: (newKey) => setSortByMetricKey(newKey),
        metricsKeyNameEntries,
        sortByMetricKey
      }),
      dataset({
        id: "dataset",
        accessorFn: (originalRow) => originalRow.dataset?.name
      }),
      hyperparameters(),
      startedAt({
        headerMessageId: "startedAt",
        headerDataTestId: "lbl_started_at",
        accessorKey: "start",
        options: {
          enableGlobalFilter: false
        }
      }),
      duration({
        headerMessageId: "duration",
        headerDataTestId: "lbl_duration",
        accessorKey: "duration",
        options: {
          enableGlobalFilter: false
        }
      }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_executors">
            <FormattedMessage id="executors" />
          </TextWithDataTestId>
        ),
        id: "executors",
        cell: ({
          row: {
            original: { executors }
          }
        }) => <ExecutorsCellContent executors={executors} />
      }
    ],
    [metricsKeyNameEntries, sortByMetricKey]
  );

  const tableData = useMemo(() => runs, [runs]);

  return isLoading ? (
    <TableLoader columnsCounter={4} />
  ) : (
    <Table
      columns={columns}
      getRowStyle={({ reached_goals: reachedGoals }) => ({
        borderLeft:
          !isEmptyObject(reachedGoals) && Object.values(reachedGoals).every(({ reached }) => reached)
            ? `4px solid ${theme.palette.success.main}`
            : undefined
      })}
      data={tableData}
      withSearch
      localization={{
        emptyMessageId: "noRuns"
      }}
      pageSize={50}
    />
  );
};

export default RunsTable;
