import Grid from "@mui/material/Grid";
import Skeleton from "@mui/material/Skeleton";
import FormattedMoney, { useMoneyFormatter } from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import LineChart from "components/LineChart";
import RawExpensesTable from "components/RawExpensesTable";
import ResourceGroupedExpensesTable from "components/ResourceGroupedExpensesTable";
import { RESOURCE_PAGE_EXPENSES_TABS, FORMATTED_MONEY_TYPES } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import ResourceRawExpensesChartTooltipBody from "./ResourceRawExpensesChartTooltipBody";
import { getData } from "./utils/getData";

const ResourceRawExpenses = ({ expenses, shownExpenses, startDate, endDate, isLoading, expensesMode }) => {
  const formatMoney = useMoneyFormatter();

  const { tableData, chartData } = getData(expenses);

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
          yScale={{
            stacked: true
          }}
          renderTooltipBody={({ slice, stacked }) => <ResourceRawExpensesChartTooltipBody slice={slice} stacked={stacked} />}
          axisLeft={{
            format: (value) => formatMoney(FORMATTED_MONEY_TYPES.COMPACT, value)
          }}
        />
      </Grid>
      <Grid item xs={12}>
        {expensesMode === RESOURCE_PAGE_EXPENSES_TABS.GROUPED && (
          <ResourceGroupedExpensesTable
            startDate={startDate}
            endDate={endDate}
            data={tableData}
            isLoading={isLoading}
            shouldShowUsageColumn={tableData.some(({ usage, usageUnit }) => !!usage && !!usageUnit)}
          />
        )}
        {expensesMode === RESOURCE_PAGE_EXPENSES_TABS.DETAILED && (
          <RawExpensesTable expenses={expenses} isLoading={isLoading} />
        )}
      </Grid>
    </Grid>
  );
};

export default ResourceRawExpenses;
