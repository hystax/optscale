import { useMemo } from "react";
import { getDifference, getUniqueValuesFromObjectsByKey } from "utils/arrays";
import { AWS_CNR } from "utils/constants";
import { formatISO } from "utils/datetime";

const getFormattedOrdinateValues = (currentValue, currentPointValue) => {
  const values = {
    y: (currentPointValue.y || 0) + currentValue.expense
  };

  if (currentValue.cloudType === AWS_CNR) {
    values.usage = (currentPointValue.usage || 0) + (currentValue.usage || 0);
    values.usageUnit = currentValue.usageUnit || currentPointValue.usageUnit;
  }

  return values;
};

export const useResourceRawExpensesChartData = ({ groupedData, expenses }) => {
  const chartData = useMemo(() => {
    // Utility data
    const uniqueDays = getUniqueValuesFromObjectsByKey(expenses, "start_date").map((item) => formatISO(item));

    // There might be multiple expenses and unit usages for the same date, but for different time. Sum that values by date.
    const formattedData = Object.entries(groupedData).reduce((result, [groupName, value]) => {
      const xValues = value.reduce((xs, item) => [...xs, item.date], []);

      // Map: [x, {...}]
      const pointsMap = new Map();

      // Chart values must be consistent, fill gaps with a default Map elements - [missingXValue, { y: 0 }]
      const diff = getDifference(uniqueDays, xValues);
      diff.forEach((missingXValue) => {
        pointsMap.set(missingXValue, {
          y: 0
        });
      });

      const data = Array.from(
        value.reduce((v, currentValue) => {
          const { date: x } = currentValue;
          const currentPointValue = v.get(x) || {};
          v.set(x, getFormattedOrdinateValues(currentValue, currentPointValue));
          return v;
        }, pointsMap),
        // TODO: add usage here
        ([x, valuesObject]) => ({ x, ...valuesObject })
      );

      return {
        ...result,
        [groupName]: data
      };
    }, {});

    // Build result chart data formatted with compliance to the chart requirements
    const resultData = Object.entries(formattedData).reduce(
      (result, [groupName, value]) => [...result, { id: groupName, data: value }],
      []
    );

    /**
     Sanitize data:
     1. Filter out items with chart points with 0 cost
     2. Sort chart points by date
     3. Sort items by sum of expenses in descending order(ids with bigger sum of expenses appear on top of others)
    */
    return resultData
      .filter((item) => item.data.sort((a, b) => (Date.parse(a.x) > Date.parse(b.x) ? 1 : -1)).some((data) => data.y !== 0))
      .sort((a, b) => (a.data.reduce((max, data) => max + data.y, 0) > b.data.reduce((max, data) => max + data.y, 0) ? 1 : -1));
  }, [expenses, groupedData]);

  return chartData;
};
