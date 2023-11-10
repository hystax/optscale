import { useIntl } from "react-intl";
import CanvasBarChart from "components/CanvasBarChart";
import KeyValueChartTooltipBody from "components/KeyValueChartTooltipBody";
import { getBandDetailsKey, getBarChartDataAndKeys, addEntityIconToTooltipKey, AXIS_FORMATS } from "utils/charts";
import { EXPENSES_SPLIT_PERIODS } from "utils/constants";
import { idx } from "utils/objects";

const ExpensesBreakdownBarChart = ({ periodType, pdfId, breakdownData, fieldTooltipText, onClick, filterBy, colorsMap }) => {
  const intl = useIntl();
  const { data, keys } = getBarChartDataAndKeys({
    keyField: "name",
    keyValue: "expense",
    indexBy: "date",
    sourceData: {
      [EXPENSES_SPLIT_PERIODS.DAILY]: breakdownData.daily,
      [EXPENSES_SPLIT_PERIODS.WEEKLY]: breakdownData.weekly,
      [EXPENSES_SPLIT_PERIODS.MONTHLY]: breakdownData.monthly
    }[periodType]
  });

  const onClickHandler =
    typeof onClick === "function"
      ? (sectionData) => {
          const { data: bandData, id: keyField } = sectionData;
          const { [getBandDetailsKey(keyField)]: details } = bandData;
          onClick(details);
        }
      : undefined;

  const renderTooltipBody = (sectionData) => {
    const { data: bandData, id: keyField } = sectionData;
    const { [getBandDetailsKey(keyField)]: details } = bandData;
    const text = fieldTooltipText ? idx(fieldTooltipText, sectionData) : intl.formatMessage({ id: keyField });
    return <KeyValueChartTooltipBody value={sectionData.value} text={addEntityIconToTooltipKey(text, details, filterBy)} />;
  };

  return (
    <CanvasBarChart
      indexBy="date"
      keys={keys}
      data={data}
      onClick={onClickHandler}
      renderTooltipBody={renderTooltipBody}
      pdfId={pdfId}
      colorsMap={colorsMap}
      axisFormat={AXIS_FORMATS.MONEY}
    />
  );
};

export default ExpensesBreakdownBarChart;
