import React, { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import FormattedMoney from "components/FormattedMoney";
import HeaderHelperCell from "components/HeaderHelperCell";
import KeyValueLabel from "components/KeyValueLabel";
import LastApplicationRunGoals from "components/LastApplicationRunGoals";
import MlApplicationsFilters from "components/MlApplicationsFilters";
import MlRunDuration from "components/MlRunDuration";
import MlRunStatus from "components/MlRunStatus";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIntervalTimeAgo } from "hooks/useIntervalTimeAgo";
import { getMlDetailsUrl, ML_APPLICATION_CREATE } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { CELL_EMPTY_VALUE } from "utils/tables";

const LastRunStatus = ({ lastRun, status }) => {
  const timeAgo = useIntervalTimeAgo(lastRun, 1);
  return (
    <CaptionedCell caption={[{ node: timeAgo, key: "time" }]}>
      <MlRunStatus status={status} />
    </CaptionedCell>
  );
};

const getColumns = () => {
  const columns = [
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
        <Link to={getMlDetailsUrl(id)} component={RouterLink}>
          {cell.getValue()}
        </Link>
      )
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
    {
      header: (
        <TextWithDataTestId dataTestId="lbl_last_run_duration">
          <FormattedMessage id="lastRunDuration" />
        </TextWithDataTestId>
      ),
      accessorKey: "last_run_duration",
      columnSelector: {
        accessor: "lastRunDuration",
        messageId: "lastRunDuration",
        dataTestId: "btn_toggle_column_last_run_durations"
      },
      cell: ({ cell }) => {
        const lastRunDuration = cell.getValue();

        return lastRunDuration === 0 ? CELL_EMPTY_VALUE : <MlRunDuration durationInSeconds={lastRunDuration} />;
      }
    },
    {
      header: (
        <HeaderHelperCell titleMessageId="goals" titleDataTestId="lbl_goals" helperMessageId="applicationGoalsDescription" />
      ),
      accessorKey: "run_goals",
      columnSelector: {
        accessor: "goals",
        messageId: "goals",
        dataTestId: "btn_toggle_column_last_run_goals"
      },
      enableSorting: false,
      cell: ({
        cell,
        row: {
          original: { goals = [] }
        }
      }) => {
        const lastRunGoals = cell.getValue();

        return isEmptyArray(goals) ? (
          CELL_EMPTY_VALUE
        ) : (
          <LastApplicationRunGoals applicationGoals={goals} lastRunGoals={lastRunGoals} />
        );
      }
    },
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
  ];

  return columns;
};

const MlApplicationsTable = ({ data, filterValues, appliedFilters, onFilterChange, isLoading }) => {
  const columns = useMemo(() => getColumns(), []);

  const tableActionBarDefinition = {
    show: true,
    definition: {
      items: [
        {
          key: "btn-create-application",
          icon: <AddOutlinedIcon />,
          messageId: "add",
          color: "success",
          variant: "contained",
          type: "button",
          dataTestId: "btn-create-application",
          link: ML_APPLICATION_CREATE,
          requiredActions: ["EDIT_PARTNER"]
        },
        {
          key: "ml-applications-filters",
          dataTestId: "ml-applications-filters",
          node: <MlApplicationsFilters appliedFilters={appliedFilters} filterValues={filterValues} onChange={onFilterChange} />,
          type: "custom"
        }
      ]
    }
  };

  return (
    <>
      {isLoading ? (
        <TableLoader columnsCounter={columns.length} showHeader />
      ) : (
        <Table
          data={data}
          columns={columns}
          actionBar={tableActionBarDefinition}
          withSearch
          columnsSelectorUID="mlApplicationsTable"
        />
      )}
    </>
  );
};

export default MlApplicationsTable;
