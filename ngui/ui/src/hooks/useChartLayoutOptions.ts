import { getHorizontalBarChartBottomTickValues, getVerticalBarChartBottomTickValues } from "utils/charts";

const BOTTOM_TICK_SIZE = 5;

export const useChartLayoutOptions = ({
  layout,
  formatValueAxis,
  valueTickValues,
  valueGridValues,
  innerWidth,
  data,
  indexBy,
  padding,
  chartTheme,
  enableGridY: enableGridYOption,
  enableGridX: enableGridXOption,
  axisBottom: axisBottomOption = {},
  axisLeft: axisLeftOption = {},
  axisRight: axisRightOption = null,
  minValue,
  maxValue,
}) => {
  let axisLeft;
  let axisBottom;
  let axisRight;

  let enableGridX;
  let enableGridY;

  let gridXValues;
  let gridYValues;

  const font = {
    fontSize: chartTheme.axis.ticks.text.fontSize,
    fontFamily: chartTheme.axis.ticks.text.fontFamily,
  };

  if (layout === "vertical") {
    axisLeft =
      axisLeftOption === null
        ? null
        : {
            tickValues: valueTickValues,
            tickSize: 0,
            tickPadding: 5,
            ...axisLeftOption,
            format: axisLeftOption.format ?? formatValueAxis,
          };

    axisRight =
      axisRightOption === null
        ? null
        : {
            tickSize: 0,
            tickPadding: 5,
            ...axisRightOption,
            format: axisRightOption.format ?? formatValueAxis,
          };

    axisBottom =
      axisBottomOption === null
        ? null
        : {
            tickSize: BOTTOM_TICK_SIZE,
            ...axisBottomOption,
            format: axisBottomOption.format,
            tickValues:
              // TODO - without innerWidth > 0 tests fail, investigate
              innerWidth > 0 &&
              getVerticalBarChartBottomTickValues({
                domain: data.map((el) => el[indexBy]),
                tickValues: axisBottomOption.tickValues ?? data.map((el) => el[indexBy]),
                format: axisBottomOption.format,
                padding,
                font,
                innerWidth,
              }),
          };

    enableGridX = enableGridYOption ?? false;
    enableGridY = enableGridXOption ?? true;

    gridYValues = valueGridValues;
  }

  if (layout === "horizontal") {
    axisLeft =
      axisLeftOption === null
        ? null
        : {
            tickSize: 0,
            tickPadding: 5,
            ...axisLeftOption,
          };

    axisRight =
      axisRightOption === null
        ? null
        : {
            tickSize: 0,
            tickPadding: 5,
            ...axisRightOption,
          };

    axisBottom =
      axisBottomOption === null
        ? null
        : {
            tickSize: BOTTOM_TICK_SIZE,
            ...axisBottomOption,
            format: axisBottomOption.format ?? formatValueAxis,
            tickValues:
              innerWidth > 0 &&
              getHorizontalBarChartBottomTickValues({
                domain: [minValue, maxValue],
                tickValues: axisBottomOption.tickValues ?? valueTickValues,
                format: axisBottomOption.format ?? formatValueAxis,
                font,
                innerWidth,
              }),
          };

    enableGridX = enableGridYOption ?? true;
    enableGridY = enableGridXOption ?? false;

    gridXValues = valueGridValues;
  }

  return {
    axisLeft,
    axisRight,
    gridYValues,
    axisBottom,
    enableGridX,
    enableGridY,
    gridXValues,
  };
};
