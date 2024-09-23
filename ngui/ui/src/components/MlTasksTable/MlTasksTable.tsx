import { useMemo, useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { Stack } from "@mui/system";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import MlTasksFilters from "components/MlTasksFilters";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsOptScaleModeEnabled } from "hooks/useIsOptScaleModeEnabled";
import { ML_TASK_CREATE } from "urls";
import { duration, metrics, mlTaskLastRun, mlTaskName } from "utils/columns";
import { OPTSCALE_MODE } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { getTasksMetricsKeyNameEntries, getFirstMetricEntryKey } from "utils/ml";

const MlTasksTable = ({ tasks, filterValues, appliedFilters, onFilterChange }) => {
  const isFinOpsEnabled = useIsOptScaleModeEnabled(OPTSCALE_MODE.FINOPS);

  const metricsKeyNameEntries = getTasksMetricsKeyNameEntries(tasks);

  const [sortByMetricKey, setSortByMetricKey] = useState(getFirstMetricEntryKey(metricsKeyNameEntries));

  const columns = useMemo(
    () => [
      mlTaskName({
        enableHiding: false
      }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_key">
            <FormattedMessage id="key" />
          </TextWithDataTestId>
        ),
        accessorKey: "key",
        enableHiding: false,
        cell: ({ cell }) => cell.getValue()
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_owner">
            <FormattedMessage id="owner" />
          </TextWithDataTestId>
        ),
        id: "owner.name",
        accessorFn: (originalRow) => originalRow.owner.name,
        columnSelector: {
          accessor: "owner",
          messageId: "owner",
          dataTestId: "btn_toggle_column_owner"
        }
      },
      mlTaskLastRun({
        columnSelector: {
          accessor: "lastRun",
          messageId: "lastRun",
          dataTestId: "btn_toggle_column_last_run"
        }
      }),
      duration({
        headerMessageId: "lastRunDuration",
        headerDataTestId: "lbl_last_run_duration",
        accessorKey: "last_run_duration",
        options: {
          columnSelector: {
            accessor: "lastRunDuration",
            messageId: "lastRunDuration",
            dataTestId: "btn_toggle_column_last_run_durations"
          }
        }
      }),
      metrics({
        accessorKey: "last_run_reached_goals",
        onSortByMetricKeyChange: (newKey) => setSortByMetricKey(newKey),
        metricsKeyNameEntries,
        sortByMetricKey,
        columnSelector: {
          accessor: "metrics",
          messageId: "metrics",
          dataTestId: "btn_toggle_column_metrics"
        }
      }),
      ...(isFinOpsEnabled
        ? [
            {
              header: (
                <TextWithDataTestId dataTestId="lbl_expenses">
                  <FormattedMessage id="expenses" />
                </TextWithDataTestId>
              ),
              id: "total_cost",
              columnSelector: {
                accessor: "expenses",
                messageId: "expenses",
                dataTestId: "btn_toggle_column_expenses"
              },
              cell: ({
                row: {
                  original: { total_cost: total, last_30_days_cost: last30DaysCost, last_run_cost: lastRunCost }
                }
              }) => (
                <>
                  <KeyValueLabel keyMessageId="lastRun" value={<FormattedMoney value={lastRunCost} />} />
                  <KeyValueLabel keyMessageId="total" value={<FormattedMoney value={total} />} />
                  <KeyValueLabel keyMessageId="last30Days" value={<FormattedMoney value={last30DaysCost} />} />
                </>
              )
            }
          ]
        : [])
    ],
    [isFinOpsEnabled, metricsKeyNameEntries, sortByMetricKey]
  );

  const data = useMemo(() => tasks, [tasks]);

  const tableActionBarDefinition = {
    show: true,
    definition: {
      items: [
        {
          key: "btn-create-task",
          icon: <AddOutlinedIcon />,
          messageId: "add",
          color: "success",
          variant: "contained",
          type: "button",
          dataTestId: "btn-create-task",
          link: ML_TASK_CREATE,
          requiredActions: ["EDIT_PARTNER"]
        }
      ]
    }
  };

  return (
    <>
      <Stack spacing={SPACING_1}>
        <div>
          <MlTasksFilters appliedFilters={appliedFilters} filterValues={filterValues} onChange={onFilterChange} />
        </div>
        <div>
          <Table
            data={data}
            columns={columns}
            actionBar={tableActionBarDefinition}
            withSearch
            localization={{
              emptyMessageId: "noTasks"
            }}
            columnsSelectorUID="mlTasksTable"
            pageSize={50}
          />
        </div>
      </Stack>
    </>
  );
};

export default MlTasksTable;
