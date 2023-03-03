import { findMaxNumber, isEmpty as isEmptyArray } from "utils/arrays";
import { minMaxDenormalize, minMaxNormalize, round } from "utils/math";

export const useMlBreakdownLines = ({ breakdown, breakdownConfig, selectedBreakdowns }) =>
  Object.entries(breakdownConfig)
    .filter(([name]) => selectedBreakdowns.includes(name))
    .map(([name, config]) => ({
      name,
      data: Object.entries(breakdown)
        .map(([xBreakdownValue, data]) => ({
          x: Number(xBreakdownValue),
          y: config.getPointValue(data)
        }))
        .filter(({ y }) => y !== null),
      config
    }))
    .filter(({ data }) => !isEmptyArray(data))
    .map(({ name, data, config }) => {
      const { formatAxis, formatValue, renderBreakdownName, maxValue } = config;

      const yValues = data.map(({ y }) => y);

      const minMax = {
        max: maxValue ?? findMaxNumber(yValues),
        min: 0
      };

      const isZeroLine = yValues.every((value) => value === 0);

      const getYValue = (rawY) => {
        if (isZeroLine) {
          return 0;
        }
        return minMaxNormalize(rawY, minMax, 1);
      };

      return {
        id: name,
        data: data.map(({ x, y }) => ({
          x,
          y: getYValue(y),
          formattedY: formatValue(y),
          formattedLineName: renderBreakdownName()
        })),
        formatAxis: (value) => {
          const getAxisValue = () => {
            if (isZeroLine) {
              return value;
            }

            return round(minMaxDenormalize(value, minMax), 2);
          };

          return formatAxis(getAxisValue());
        }
      };
    });
