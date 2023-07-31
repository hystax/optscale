import { getBarChartBottomTickValues } from "utils/charts";

export const useChartLayoutOptions = ({
  layout,
  formatAxis,
  tickValues,
  chartWidth,
  data,
  indexBy,
  padding,
  chartTheme,
  gridValues,
  enableGridY: enableGridYOption,
  enableGridX: enableGridXOption,
  axisBottom: axisBottomOption,
  axisLeft: axisLeftOption
}) => {
  let axisLeft = {};
  let axisBottom = {};
  let enableGridX;
  let enableGridY;
  let gridXValues;
  let gridYValues;

  if (layout === "vertical") {
    axisLeft =
      axisLeftOption || axisLeftOption === null
        ? axisLeftOption
        : {
            format: formatAxis,
            tickSize: 0,
            tickPadding: 5,
            tickValues
          };

    const bottomTickSize = 5;

    // TODO - without chartWidth > 0 tests fail, investigate
    const bottomTickValues =
      chartWidth > 0 &&
      getBarChartBottomTickValues({
        data,
        indexBy,
        padding,
        font: {
          fontSize: chartTheme.axis.ticks.text.fontSize,
          fontFamily: chartTheme.axis.ticks.text.fontFamily
        },
        innerWidth: chartWidth
      });

    axisBottom =
      axisBottomOption || axisBottomOption === null
        ? axisBottomOption
        : {
            ...axisBottom,
            tickSize: bottomTickSize,
            tickValues: bottomTickValues
          };

    enableGridX = enableGridYOption ?? false;
    enableGridY = enableGridXOption ?? true;

    gridYValues = gridValues;
  }

  if (layout === "horizontal") {
    axisBottom =
      axisBottomOption || axisBottomOption === null
        ? axisBottomOption
        : {
            format: formatAxis,
            tickSize: 0,
            tickPadding: 5,
            tickValues
          };

    enableGridX = enableGridYOption ?? true;
    enableGridY = enableGridXOption ?? false;

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
