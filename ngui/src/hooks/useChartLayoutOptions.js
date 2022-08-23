import { calculateOverflowSettings } from "utils/charts";

export const useChartLayoutOptions = ({
  layout,
  formatAxis,
  tickValues,
  chartWidth,
  data,
  indexBy,
  padding,
  chartTheme,
  gridValues
}) => {
  let axisLeft = {};
  let axisBottom = {};
  let enableGridX = false;
  let enableGridY = true;
  let gridXValues;
  let gridYValues;

  if (layout === "vertical") {
    axisLeft = {
      format: formatAxis,
      tickSize: 0,
      tickPadding: 5,
      tickValues
    };
    const bottomTickSize = 5;

    // TODO - without chartWidth > 0 tests fail, investigate
    const bottomTickValues =
      chartWidth > 0 &&
      calculateOverflowSettings({
        data,
        indexBy,
        padding,
        font: {
          fontSize: chartTheme.axis.ticks.text.fontSize,
          fontFamily: chartTheme.axis.ticks.text.fontFamily
        },
        chartWidth
      });

    axisBottom = {
      ...axisBottom,
      tickSize: bottomTickSize,
      tickValues: bottomTickValues
    };

    gridYValues = gridValues;
  }

  if (layout === "horizontal") {
    axisBottom = {
      format: formatAxis,
      tickSize: 0,
      tickPadding: 5,
      tickValues
    };
    enableGridX = true;
    enableGridY = false;
    gridXValues = gridValues;
  }

  return {
    axisLeft,
    gridYValues,
    axisBottom,
    enableGridX,
    enableGridY,
    gridXValues
  };
};
