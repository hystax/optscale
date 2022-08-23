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
    Header: <TextWithDataTestId dataTestId={`lbl_${field}`}>{field}</TextWithDataTestId>,
    accessor: field,
    isStatic: STATIC_RAW_EXPENSES_COLUMNS.indexOf(field) !== -1,
    columnsSelector: {
      title: field,
      dataTestId: `btn_toggle_column_${field}`
    },
    Cell: ({ cell: { value } }) => value
  }));

const RawExpensesTable = ({ expenses, isLoading }) => {
  // patching expenses: all rows object-type props replacing with json
  const data = useMemo(
    () =>
      expenses.map((e) =>
        Object.fromEntries(Object.entries(e).map(([key, value]) => [key, isObject(value) ? JSON.stringify(value) : value]))
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
      order={STATIC_RAW_EXPENSES_COLUMNS}
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
