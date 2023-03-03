import React, { useMemo } from "react";
import PropTypes from "prop-types";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { RAW_EXPENSES } from "reducers/columns";
import { STATIC_RAW_EXPENSES_COLUMNS } from "reducers/columns/utils";
import { isObject } from "utils/objects";

const getUniqueFields = (expenses) => expenses.reduce((res, curr) => [...new Set([...res, ...Object.keys(curr)])], []).sort();

const buildColumnsDefinition = (fields) =>
  fields.map((field) => ({
    header: <TextWithDataTestId dataTestId={`lbl_${field}`}>{field}</TextWithDataTestId>,
    accessorKey: field,
    enableHiding: !STATIC_RAW_EXPENSES_COLUMNS.includes(field),
    columnSelector: {
      accessor: field,
      title: field,
      dataTestId: `btn_toggle_column_${field}`
    },
    cell: ({ cell }) => cell.getValue()
  }));

const RawExpensesTable = ({ expenses, isLoading }) => {
  const data = useMemo(
    () =>
      expenses.map((expense) =>
        Object.fromEntries(
          // Stringify all the object-type expenses props
          Object.entries(expense).map(([key, value]) => [key, isObject(value) ? JSON.stringify(value) : value])
        )
      ),
    [expenses]
  );

  const columns = useMemo(() => buildColumnsDefinition(getUniqueFields(expenses)), [expenses]);

  return isLoading ? (
    <TableLoader columnsCounter={1} />
  ) : (
    <Table
      dataTestIds={{
        searchInput: "input_search",
        searchButton: "btn_search",
        deleteSearchButton: "btn_delete_search",
        infoArea: {
          totalKey: "lbl_total",
          totalValue: "lbl_total_value",
          displayedKey: "lbl_displayed",
          displayedValue: "lbl_displayed_value"
        },
        columnsSelector: {
          button: "btn_columns_selector",
          clear: "btn_select_clear_all"
        }
      }}
      data={data}
      columns={columns}
      localization={{
        emptyMessageId: "noExpenses"
      }}
      columnOrder={STATIC_RAW_EXPENSES_COLUMNS}
      pageSize={50}
      withSearch
      counters={{ showCounters: true }}
      columnsSelectorUID={RAW_EXPENSES}
    />
  );
};

RawExpensesTable.propTypes = {
  expenses: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default RawExpensesTable;
