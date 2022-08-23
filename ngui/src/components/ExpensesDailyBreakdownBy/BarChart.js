import React from "react";
import PropTypes from "prop-types";
import BreakdownLabel from "components/BreakdownLabel";
import CanvasBarChart from "components/CanvasBarChart";
import KeyValueChartTooltipBody from "components/KeyValueChartTooltipBody";
import { AXIS_FORMATS, getBandDetailsKey, getBarChartDataAndKeys } from "utils/charts";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES } from "utils/constants";
import { EN_FORMAT_SHORT_YEAR, formatUTC } from "utils/datetime";

const BarChart = ({ breakdown, breakdownBy, isLoading = false }) => {
  const { keys, data } = getBarChartDataAndKeys({
    keyField: "id",
    keyValue: "cost",
    indexBy: "date",
    formatIndexByValue: (value) => formatUTC(value, EN_FORMAT_SHORT_YEAR),
    sourceData: breakdown
  });

  return (
    <CanvasBarChart
      indexBy="date"
      keys={keys}
      data={data}
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

BarChart.propTypes = {
  breakdown: PropTypes.object.isRequired,
  breakdownBy: PropTypes.oneOf(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES).isRequired,
  isLoading: PropTypes.bool
};

export default BarChart;
