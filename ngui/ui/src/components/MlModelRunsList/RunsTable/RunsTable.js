import React, { useMemo, useState } from "react";
import { Link } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useParams } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import CollapsableTableCell from "components/CollapsableTableCell";
import { useMoneyFormatter } from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import MlRunStatusCell from "components/MlRunStatusCell";
import MlRunStatusHeaderCell from "components/MlRunStatusHeaderCell";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getMlModelRunUrl, getMlRunsetDetailsUrl } from "urls";
import { duration, goals, startedAt } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { formatRunFullName, getFirstGoalEntryKey, getRunsGoalsKeyNameEntries } from "utils/ml";
import { isEmpty as isEmptyObject } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";

const RunsTable = ({ runs }) => {
  const theme = useTheme();

  const { modelId } = useParams();

  const formatMoney = useMoneyFormatter();

  const goalsKeyNameEntries = getRunsGoalsKeyNameEntries(runs);

  const [sortByGoalKey, setSortByGoalKey] = useState(getFirstGoalEntryKey(goalsKeyNameEntries));

  const columns = useMemo(() => {
    const getNameString = ({ number, name }) => formatRunFullName(number, name);

    return [
      {
        header: <TextWithDataTestId dataTestId="lbl_#">#</TextWithDataTestId>,
        id: "runName",
        accessorFn: ({ number, name }) => getNameString({ number, name }),
        defaultSort: "desc",
        sortingFn: "alphanumeric",
        globalFilterFn: (runName, filterValue, { row }) => {
          const search = filterValue.toLocaleLowerCase();

          const {
            original: { runset: { name: runsetName = "" } = {} }
          } = row;

          return [runName, runsetName].some((str) => str.toLocaleLowerCase().includes(search));
        },
        cell: ({ cell, row: { original } }) => {
          const { id, runset } = original;

          return (
            <CaptionedCell
              caption={
                runset
                  ? [
                      {
                        node: (
                          <KeyValueLabel
                            typographyProps={{
                              variant: "caption"
                            }}
                            messageId="runset"
                            value={
                              <Link to={getMlRunsetDetailsUrl(runset.id)} component={RouterLink}>
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
              <Link to={getMlModelRunUrl(modelId, id)} component={RouterLink}>
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
      goals({
        headerMessageId: "goals",
        headerDataTestId: "lbl_goals",
        accessorKey: "reached_goals",
        onSortByGoalKeyChange: (newKey) => setSortByGoalKey(newKey),
        goalsKeyNameEntries,
        sortByGoalKey
      }),
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
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_tags">
            <FormattedMessage id="tags" />
          </TextWithDataTestId>
        ),
        id: "tags",
        accessorFn: ({ tags }) =>
          Object.entries(tags || {})
            .map(([key, val]) => `${key}: ${val}`)
            .join(" "),
        enableSorting: false,
        cell: ({
          row: {
            original: { tags = {} }
          }
        }) => (isEmptyObject(tags) ? CELL_EMPTY_VALUE : <CollapsableTableCell maxRows={5} tags={tags} />)
      },
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
  }, [modelId, formatMoney, goalsKeyNameEntries, sortByGoalKey]);

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

RunsTable.propTypes = {
  runs: PropTypes.array
};

export default RunsTable;
