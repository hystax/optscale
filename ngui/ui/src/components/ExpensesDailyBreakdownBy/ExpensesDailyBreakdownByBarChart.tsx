import BreakdownLabel from "components/BreakdownLabel";
import CanvasBarChart from "components/CanvasBarChart";
import KeyValueChartTooltipBody from "components/KeyValueChartTooltipBody";
import { AXIS_FORMATS, getBandDetailsKey, getBarChartDataAndKeys } from "utils/charts";
import { EXPENSES_SPLIT_PERIODS } from "utils/constants";
import { getResourceExpensesSplits } from "utils/getResourceExpensesSplits";

const ExpensesDailyBreakdownByBarChart = ({
  breakdown,
  breakdownBy,
  split = EXPENSES_SPLIT_PERIODS.DAILY,
  isLoading = false,
  dataTestId
}) => {
  const { keys, data } = getBarChartDataAndKeys({
    keyField: "id",
    keyValue: "cost",
    indexBy: "date",
    sourceData: breakdown
  });

  const dataSplits = getResourceExpensesSplits(data);

  return (
    <CanvasBarChart
      dataTestId={dataTestId}
      indexBy="date"
      keys={keys}
      data={dataSplits[split]}
      renderTooltipBody={(sectionData) => {
        const { data: bandData, id: keyField, value } = sectionData;
        const { [getBandDetailsKey(keyField)]: details } = bandData;

        return <KeyValueChartTooltipBody value={value} text={<BreakdownLabel breakdownBy={breakdownBy} details={details} />} />;
      }}
      isLoading={isLoading}
      axisFormat={AXIS_FORMATS.MONEY}
    />
  );
};

export default ExpensesDailyBreakdownByBarChart;
