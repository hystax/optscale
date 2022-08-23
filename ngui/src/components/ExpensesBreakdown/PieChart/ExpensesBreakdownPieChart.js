import React from "react";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
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

ExpensesBreakdownPieChart.propTypes = {
  filteredBreakdown: PropTypes.array.isRequired,
  getCustomDetails: PropTypes.func.isRequired,
  filterBy: PropTypes.string,
  onClick: PropTypes.func,
  colorsMap: PropTypes.object,
  getShouldApplyHoverStyles: PropTypes.func.isRequired
};

export default ExpensesBreakdownPieChart;
