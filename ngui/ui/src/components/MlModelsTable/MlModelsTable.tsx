import { useMemo, useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import Link from "@mui/material/Link";
import { Stack } from "@mui/system";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import MlModelsFilters from "components/MlModelsFilters";
import MlRunStatus from "components/MlRunStatus";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIntervalTimeAgo } from "hooks/useIntervalTimeAgo";
import { getMlModelDetailsUrl, ML_MODEL_CREATE } from "urls";
import { duration, goals as goalsColumn } from "utils/columns";
import { SPACING_1 } from "utils/layouts";
import { getModelsGoalsKeyNameEntries, getFirstGoalEntryKey } from "utils/ml";

const LastRunStatus = ({ lastRun, status }) => {
  const timeAgo = useIntervalTimeAgo(lastRun, 1);
  return (
    <CaptionedCell caption={[{ node: timeAgo, key: "time" }]}>
      <MlRunStatus status={status} />
    </CaptionedCell>
  );
};

const MlModelsTable = ({ models, filterValues, appliedFilters, onFilterChange }) => {
  const goalsKeyNameEntries = getModelsGoalsKeyNameEntries(models);

  const [sortByGoalKey, setSortByGoalKey] = useState(getFirstGoalEntryKey(goalsKeyNameEntries));

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        enableHiding: false,
        cell: ({
          row: {
            original: { id }
          },
          cell
        }) => (
          <Link to={getMlModelDetailsUrl(id)} component={RouterLink}>
            {cell.getValue()}
          </Link>
        )
      },
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
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_last_run">
            <FormattedMessage id="lastRun" />
          </TextWithDataTestId>
        ),
        id: "last_run",
        columnSelector: {
          accessor: "lastRun",
          messageId: "lastRun",
          dataTestId: "btn_toggle_column_last_run"
        },
        cell: ({ row: { original } }) =>
          original.last_run === 0 ? (
            <FormattedMessage id="never" />
          ) : (
            <LastRunStatus lastRun={original.last_run} status={original.status} />
          )
      },
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
      goalsColumn({
        headerMessageId: "goals",
        headerDataTestId: "lbl_goals",
        helperMessageId: "modelGoalsDescription",
        accessorKey: "last_run_reached_goals",
        onSortByGoalKeyChange: (newKey) => setSortByGoalKey(newKey),
        goalsKeyNameEntries,
        sortByGoalKey,
        columnSelector: {
          accessor: "goals",
          messageId: "goals",
          dataTestId: "btn_toggle_column_last_run_goals"
        }
      }),
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
            <KeyValueLabel messageId="lastRun" value={<FormattedMoney value={lastRunCost} />} />
            <KeyValueLabel messageId="total" value={<FormattedMoney value={total} />} />
            <KeyValueLabel messageId="last30Days" value={<FormattedMoney value={last30DaysCost} />} />
          </>
        )
      }
    ],
    [goalsKeyNameEntries, sortByGoalKey]
  );

  const data = useMemo(() => models, [models]);

  const tableActionBarDefinition = {
    show: true,
    definition: {
      items: [
        {
          key: "btn-create-model",
          icon: <AddOutlinedIcon />,
          messageId: "add",
          color: "success",
          variant: "contained",
          type: "button",
          dataTestId: "btn-create-model",
          link: ML_MODEL_CREATE,
          requiredActions: ["EDIT_PARTNER"]
        }
      ]
    }
  };

  return (
    <>
      <Stack spacing={SPACING_1}>
        <div>
          <MlModelsFilters appliedFilters={appliedFilters} filterValues={filterValues} onChange={onFilterChange} />
        </div>
        <div>
          <Table
            data={data}
            columns={columns}
            actionBar={tableActionBarDefinition}
            withSearch
            localization={{
              emptyMessageId: "noModels"
            }}
            columnsSelectorUID="mlModelsTable"
            pageSize={50}
          />
        </div>
      </Stack>
    </>
  );
};

export default MlModelsTable;
