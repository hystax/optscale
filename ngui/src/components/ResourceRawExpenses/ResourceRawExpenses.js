import React, { useMemo } from "react";
import Grid from "@mui/material/Grid";
import Skeleton from "@mui/material/Skeleton";
import PropTypes from "prop-types";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import LineChart from "components/LineChart";
import RawExpensesTable from "components/RawExpensesTable";
import ResourceGroupedExpensesTable from "components/ResourceGroupedExpensesTable";
import { RESOURCE_PAGE_EXPENSES_TABS, FORMATTED_MONEY_TYPES } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import ResourceRawExpensesChartTooltipBody from "./ResourceRawExpensesChartTooltipBody";
import { useResourceRawExpensesChartData } from "./useResourceRawExpensesChartData";
import { useResourceRawExpensesGroupedData } from "./useResourceRawExpensesGroupedData";

const ResourceRawExpenses = ({ expenses, shownExpenses, startDate, endDate, isLoading, expensesMode }) => {
  const groupedData = useResourceRawExpensesGroupedData({ expenses });
  const chartData = useResourceRawExpensesChartData({ groupedData, expenses });

  const groupedTableData = useMemo(
    () =>
      Object.entries(groupedData)
        .map(([categoryName, categoryPayload]) => ({
          category: categoryName,
          expenses: categoryPayload.reduce((expensesSum, { expense }) => expensesSum + expense, 0),
          ...(categoryPayload.some(({ usage, usageUnit }) => !!usage && !!usageUnit)
            ? {
                usage: categoryPayload.reduce((usageSum, { usage = 0 }) => usageSum + usage, 0),
                usageUnit: categoryPayload.find(({ usageUnit }) => Boolean(usageUnit)).usageUnit
              }
            : {})
        }))
        .filter(({ expenses: expensesSum }) => expensesSum !== 0),
    [groupedData]
  );

  return (
    <Grid container spacing={SPACING_2}>
      <Grid item xs={12}>
        {isLoading ? (
          <Skeleton width={100} />
        ) : (
          <KeyValueLabel
            messageId="expenses"
            value={<FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={shownExpenses} />}
            dataTestIds={{
              value: "lbl_expenses_value",
              key: "lbl_expenses"
            }}
          />
        )}
      </Grid>
      <Grid item xs={12}>
        <LineChart
          dataTestId="chart_expenses"
          data={chartData}
          isLoading={isLoading}
          stacked
          renderTooltipBody={ResourceRawExpensesChartTooltipBody}
          axisLeft={{
            format: (value) => <FormattedMoney value={value} type={FORMATTED_MONEY_TYPES.COMPACT} />
          }}
        />
      </Grid>
      <Grid item xs={12}>
        {expensesMode === RESOURCE_PAGE_EXPENSES_TABS.GROUPED && (
          <ResourceGroupedExpensesTable
            startDate={startDate}
            endDate={endDate}
            data={groupedTableData}
            isLoading={isLoading}
            shouldShowUsageColumn={groupedTableData.some(({ usage, usageUnit }) => !!usage && !!usageUnit)}
          />
        )}
        {expensesMode === RESOURCE_PAGE_EXPENSES_TABS.DETAILED && (
          <RawExpensesTable expenses={expenses} isLoading={isLoading} />
        )}
      </Grid>
    </Grid>
  );
};

ResourceRawExpenses.propTypes = {
  expenses: PropTypes.array.isRequired,
  shownExpenses: PropTypes.number.isRequired,
  startDate: PropTypes.number.isRequired,
  endDate: PropTypes.number.isRequired,
  expensesMode: PropTypes.oneOf(Object.values(RESOURCE_PAGE_EXPENSES_TABS)).isRequired,
  isLoading: PropTypes.bool
};

export default ResourceRawExpenses;
