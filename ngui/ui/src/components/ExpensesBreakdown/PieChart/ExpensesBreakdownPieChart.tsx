import { useTheme } from "@mui/material/styles";
import KeyValueChartTooltipBody from "components/KeyValueChartTooltipBody";
import PieChart from "components/PieChart";
import { getExpensesPieChartOptions, addEntityIconToTooltipKey } from "utils/charts";

const ExpensesBreakdownPieChart = ({
  filteredBreakdown,
  colorsMap,
  filterBy,
  getCustomDetails,
  getShouldApplyHoverStyles,
  onClick
}) => {
  const theme = useTheme();

  const pieChartOptions = getExpensesPieChartOptions({
    sourceArray: filteredBreakdown,
    onClick,
    customDetails: getCustomDetails,
    shouldApplyHoverStyles: getShouldApplyHoverStyles,
    colors: theme.palette.chart
  });

  const renderTooltipBody = (sectionData) => {
    const {
      value,
      label,
      data: { details }
    } = sectionData;
    return <KeyValueChartTooltipBody value={value} text={addEntityIconToTooltipKey(label, details, filterBy)} />;
  };

  return (
    <PieChart
      colorsMap={colorsMap}
      onClick={pieChartOptions.onClick}
      shouldApplyHoverStyles={pieChartOptions.shouldApplyHoverStyles}
      palette={pieChartOptions.palette}
      data={pieChartOptions.data}
      style={{ height: 40 }}
      renderTooltipBody={renderTooltipBody}
    />
  );
};

export default ExpensesBreakdownPieChart;
