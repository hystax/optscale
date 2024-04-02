import { useMemo, useState } from "react";
import { Link } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import { useMoneyFormatter } from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import MlRunStatusCell from "components/MlRunStatusCell";
import MlRunStatusHeaderCell from "components/MlRunStatusHeaderCell";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getMlTaskRunUrl, getMlRunsetDetailsUrl } from "urls";
import { duration, startedAt, hyperparameters, dataset, metrics, tags } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { formatRunFullName, getFirstMetricEntryKey, getRunsReachedGoalsKeyNameEntries } from "utils/ml";
import { isEmpty as isEmptyObject } from "utils/objects";

const RunsTable = ({ runs }) => {
  const theme = useTheme();

  const formatMoney = useMoneyFormatter();

  const metricsKeyNameEntries = getRunsReachedGoalsKeyNameEntries(runs);

  const [sortByMetricKey, setSortByMetricKey] = useState(getFirstMetricEntryKey(metricsKeyNameEntries));

  const columns = useMemo(() => {
    const getNameString = ({ number, name }) => formatRunFullName(number, name);

    return [
      {
        header: <TextWithDataTestId dataTestId="lbl_#">#</TextWithDataTestId>,
        id: "runName",
        accessorFn: ({ number, name }) => getNameString({ number, name }),
        defaultSort: "desc",
        sortingFn: "alphanumeric",
        searchFn: (runName, filterValue, { row }) => {
          const search = filterValue.toLocaleLowerCase();

          const {
            original: { runset: { name: runsetName = "" } = {} }
          } = row;

          return [runName, runsetName].some((str) => str.toLocaleLowerCase().includes(search));
        },
        cell: ({ cell, row: { original } }) => {
          const { id: runId, runset, task_id: taskId } = original;

          return (
            <CaptionedCell
              caption={
                runset
                  ? [
                      {
                        node: (
                          <KeyValueLabel
                            variant="caption"
                            keyMessageId="runset"
                            value={
                              <Link to={getMlRunsetDetailsUrl(runset?.id)} component={RouterLink}>
                                {runset.name}
                              </Link>
                            }
                          />
                        ),
                        key: "template"
                      }
                    ]
                  : null
              }
            >
              <Link to={getMlTaskRunUrl(taskId, runId)} component={RouterLink}>
                {cell.getValue()}
              </Link>
            </CaptionedCell>
          );
        }
      },
      {
        header: <MlRunStatusHeaderCell />,
        accessorKey: "status",
        cell: ({
          cell,
          row: {
            original: { reason }
          }
        }) => <MlRunStatusCell status={cell.getValue()} reason={reason} />
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
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_expenses">
            <FormattedMessage id="expenses" />
          </TextWithDataTestId>
        ),
        accessorKey: "cost",
        accessorFn: ({ cost }) => formatMoney(FORMATTED_MONEY_TYPES.COMMON, cost),
        cell: ({ cell }) => cell.getValue()
      },
      tags({
        id: "tags",
        accessorFn: (originalRow) =>
          Object.entries(originalRow.tags ?? {})
            .map(([key, val]) => `${key}: ${val}`)
            .join(" "),
        getTags: (originalRow) => originalRow.tags
      }),
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
      })
    ];
  }, [formatMoney, metricsKeyNameEntries, sortByMetricKey]);

  const tableData = useMemo(() => runs, [runs]);

  return (
    <Table
      withSearch
      data={tableData}
      columns={columns}
      getRowStyle={({ reached_goals: reachedGoals }) => ({
        borderLeft:
          !isEmptyObject(reachedGoals) && Object.values(reachedGoals).every(({ reached }) => reached)
            ? `4px solid ${theme.palette.success.main}`
            : undefined
      })}
      pageSize={50}
      localization={{
        emptyMessageId: "noRuns"
      }}
    />
  );
};

export default RunsTable;
