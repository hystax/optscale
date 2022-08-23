import React, { useMemo } from "react";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CircleLabel from "components/CircleLabel";
import ExpensesTableHeader from "components/ExpensesTableHeader";
import FormattedMoney from "components/FormattedMoney";
import ResourceUsageFormattedNumber from "components/ResourceUsageFormattedNumber";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getColorScale } from "utils/charts";
import { ONE_CENT, FORMATTED_MONEY_TYPES } from "utils/constants";

const ResourceGroupedExpensesTable = ({ data, isLoading, startDate, endDate, shouldShowUsageColumn = false }) => {
  const theme = useTheme();

  const tableData = useMemo(() => data, [data]);

  const columns = useMemo(() => {
    const colorScale = getColorScale(theme.palette.chart);
    return [
      {
        accessor: "category",
        Header: (
          <TextWithDataTestId dataTestId="lbl_table_category">
            <FormattedMessage id="category" />
          </TextWithDataTestId>
        ),
        Cell: ({ row: { original = {} } }) => (
          <CircleLabel figureColor={colorScale(original.category)} label={original.category} textFirst={false} />
        )
      },
      {
        accessor: "expenses",
        Header: (
          <TextWithDataTestId dataTestId="lbl_table_expenses">
            <ExpensesTableHeader startDate={startDate} endDate={endDate} />
          </TextWithDataTestId>
        ),
        Cell: ({ row: { original = {} } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.expenses} />,
        defaultSort: "desc"
      },
      ...(shouldShowUsageColumn
        ? [
            {
              accessor: "usage",
              Header: (
                <TextWithDataTestId dataTestId="lbl_table_usage">
                  <FormattedMessage id="usage" />
                </TextWithDataTestId>
              ),
              Cell: ({ row: { original = {} } }) =>
                original.usage && original.usageUnit && original.expenses >= ONE_CENT ? (
                  <ResourceUsageFormattedNumber usage={original.usage} unit={original.usageUnit} />
                ) : (
                  "-"
                )
            }
          ]
        : [])
    ];
  }, [endDate, shouldShowUsageColumn, startDate, theme.palette.chart]);

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} />
  ) : (
    <Table
      dataTestIds={{
        container: "table_grouped",
        searchInput: "input_search"
      }}
      withSearch
      data={tableData}
      columns={columns}
      localization={{
        emptyMessageId: "noExpenses"
      }}
    />
  );
};

ResourceGroupedExpensesTable.propTypes = {
  data: PropTypes.array.isRequired,
  isLoading: PropTypes.bool,
  startDate: PropTypes.number,
  endDate: PropTypes.number,
  shouldShowUsageColumn: PropTypes.bool
};

export default ResourceGroupedExpensesTable;
