import { findMaxNumber, findMinNumber, isEmpty as isEmptyArray } from "utils/arrays";
import { denormalize as denormalizeUtil, normalize as normalizeUtil, round } from "utils/math";

const UNITLESS = "uniteless";

export const BREAKDOWN_LINE_UNIT = Object.freeze({
  PERCENT: "percent",
  MEBIBYTE: "mebibyte"
});

export const useMlBreakdownLines = ({ breakdown, breakdownConfig, selectedBreakdowns }) => {
  const breakdowns = breakdownConfig
    .filter(({ name }) => selectedBreakdowns.includes(name))
    .map(({ name, getPointValue, unit = UNITLESS, formatValue, formatAxis, renderBreakdownName }) => {
      const data = Object.entries(breakdown)
        .map(([second, breakdownData]) => ({
          x: Number(second),
          y: getPointValue(breakdownData)
        }))
        .filter(({ y }) => y !== null);

      const getMinMaxValues = () => {
        if (unit === BREAKDOWN_LINE_UNIT.PERCENT) {
          return {
            maxValue: 100,
            minValue: 0,
            absMaxValue: 100
          };
        }

        const yValues = data.map(({ y }) => y);
        const absYValues = yValues.map(Math.abs);

        return {
          maxValue: findMaxNumber(yValues),
          minValue: findMinNumber(yValues),
          absMaxValue: findMaxNumber(absYValues)
        };
      };

      return {
        name,
        data,
        unit,
        formatValue,
        formatAxis,
        renderBreakdownName,
        ...getMinMaxValues()
      };
    });

  const unitAbsoluteMaxMap = Object.fromEntries(
    Object.values(BREAKDOWN_LINE_UNIT).map((unit) => {
      const maxValues = breakdowns
        .filter(({ unit: breakdownUnit }) => breakdownUnit === unit)
        .map(({ absMaxValue }) => absMaxValue);

      return [unit, findMaxNumber(maxValues)];
    })
  );

  const lines = breakdowns
    .filter(({ data }) => !isEmptyArray(data))
    .map(({ name, data, maxValue, minValue, absMaxValue, unit, formatValue, renderBreakdownName, formatAxis }) => {
      const getAbsMaxValue = () => (unit === UNITLESS ? absMaxValue : unitAbsoluteMaxMap[unit]);

      const isZeroLine = minValue === 0 && maxValue === 0;
      const isPositiveLine = !isZeroLine && minValue >= 0 && maxValue >= 0;
      const isNegativeLine = !isZeroLine && minValue <= 0 && maxValue <= 0;

      const getNormalizationFunctions = () => {
        const getNormalizationRange = () => {
          if (isNegativeLine) {
            return [-1, 0];
          }
          if (isPositiveLine) {
            return [0, 1];
          }
          return [-1, 1];
        };

        const getMinMaxNormalizationValues = () => {
          const absMax = getAbsMaxValue();

          if (isNegativeLine) {
            return [-absMax, 0];
          }
          if (isPositiveLine) {
            return [0, absMax];
          }
          return [-absMax, absMax];
        };

        return {
          normalize: (value) =>
            isZeroLine ? 0 : normalizeUtil(value, getMinMaxNormalizationValues(), getNormalizationRange()),
          denormalize: (value) =>
            isZeroLine ? value : denormalizeUtil(value, getMinMaxNormalizationValues(), getNormalizationRange())
        };
      };

      const { normalize, denormalize } = getNormalizationFunctions();

      return {
        id: name,
        data: data.map(({ x, y }) => ({
          x,
          y: normalize(y),
          formattedY: formatValue(y),
          formattedLineName: renderBreakdownName()
        })),
        formatAxis: (value) => {
          const getAxisValue = () => round(denormalize(value), 2);

          return formatAxis(getAxisValue());
        }
      };
    });

  return lines;
};
