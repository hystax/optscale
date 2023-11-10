import { intl } from "translations/react-intl-config";
import { getDifference, getUniqueValuesFromObjectsByKey } from "utils/arrays";
import { AWS_CNR, AZURE_CNR, ALIBABA_CNR, NEBIUS as NEBIUS_DATA_SOURCE, NOT_SET_CLOUD_TYPE } from "utils/constants";
import { formatISO } from "utils/datetime";

const AWS = Object.freeze({
  LINE_ITEM_DESCRIPTION: "lineItem/LineItemDescription",
  LINE_ITEM_BLENDED_RATE: "lineItem/BlendedRate",
  PRICING_UNIT: "pricing/unit"
});

const ALIBABA = Object.freeze({
  BILLING_ITEM: "BillingItem"
});

const NEBIUS = Object.freeze({
  SKU_NAME: "sku_name",
  COST: "cost",
  PRICING_QUANTITY: "pricing_quantity",
  PRICING_UNIT: "pricing_unit"
});

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

const getCloudType = (item = {}) => {
  if (item[AWS.LINE_ITEM_DESCRIPTION]) {
    return AWS_CNR;
  }
  if (item.meter_details?.meter_name) {
    return AZURE_CNR;
  }
  if (item[ALIBABA.BILLING_ITEM]) {
    return ALIBABA_CNR;
  }
  if (item[NEBIUS.SKU_NAME]) {
    return NEBIUS_DATA_SOURCE;
  }
  return NOT_SET_CLOUD_TYPE;
};

const getCategory = (cloudType, item) =>
  ({
    [AWS_CNR]: item?.[AWS.LINE_ITEM_DESCRIPTION],
    [AZURE_CNR]: item?.meter_details?.meter_name,
    [ALIBABA_CNR]: item?.[ALIBABA.BILLING_ITEM],
    [NEBIUS_DATA_SOURCE]: item?.[NEBIUS.SKU_NAME],
    // If we could not identify cloud_type by the raw_data -> place it in the default group - "Total expenses"
    [NOT_SET_CLOUD_TYPE]: intl.formatMessage({ id: "totalExpenses" })
  })[cloudType];

const getUsage = (cloudType, item) =>
  (
    ({
      [AWS_CNR]: () => {
        const lineItemBlendedRate = +item[AWS.LINE_ITEM_BLENDED_RATE];
        const pricingUnit = item[AWS.PRICING_UNIT];
        if (!lineItemBlendedRate || !pricingUnit) {
          return {
            usage: 0,
            usageUnit: undefined
          };
        }
        const cost = item.cost ?? 0;
        const usage = lineItemBlendedRate === 0 ? 0 : cost / lineItemBlendedRate;
        return {
          usage,
          usageUnit: pricingUnit
        };
      },
      [NEBIUS_DATA_SOURCE]: () => ({
        usage: +item[NEBIUS.PRICING_QUANTITY],
        usageUnit: item[NEBIUS.PRICING_UNIT]
      })
    })[cloudType] ?? (() => {})
  )();

const buildData = (cloudType, item) => ({
  date: formatISO(item.start_date),
  expense: item.cost ?? 0,
  ...getUsage(cloudType, item)
});

/**
  Build an object grouped by target field value.
  At this step values can be inconsistent, it is not guaranteed that there is data for all dates
  
  {
    expenseCategoryName1: [
      { date: d1, expense: e1 },
      { date: d1, expense: e1_1 },
      { date: d3, expense: e2 }
    ],
    expenseCategoryName2: [
      { date: d1, expense: e3 },
      { date: d2, expense: e4 },
      { date: d3, expense: e5 }
    ],
    expenseCategoryName3: [
      { date: d2, expense: e6 },
      { date: d3, expense: e7 },
      { date: d3, expense: e7_1 }
    ]
  }
*/

const prepareTableData = (groupedExpenses) =>
  Object.entries(groupedExpenses)
    .map(([categoryName, categoryPayload]) => ({
      category: categoryName,
      expenses: categoryPayload.reduce((expensesSum, { expense }) => expensesSum + expense, 0),
      ...(categoryPayload.some(({ usage, usageUnit }) => !!usage && !!usageUnit)
        ? {
            usage: categoryPayload.reduce((usageSum, { usage = 0 }) => usageSum + usage, 0),
            usageUnit: categoryPayload.find(({ usageUnit }) => Boolean(usageUnit)).usageUnit
          }
        : {})
    }))
    .filter(({ expenses: expensesSum }) => expensesSum !== 0);

const prepareChartData = (groupedData, expenses) => {
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
};

export const getData = (expenses) => {
  // dataSourceType is always the same, determine it once
  const firstItem = expenses[0];
  const dataSourceType = getCloudType(firstItem);

  const groupedExpenses = expenses.reduce((result, item) => {
    const category = getCategory(dataSourceType, item);
    const data = buildData(dataSourceType, item);

    return {
      ...result,
      [category]: [...(result[category] ?? []), data]
    };
  }, {});

  const tableData = prepareTableData(groupedExpenses);

  const chartData = prepareChartData(groupedExpenses, expenses);

  return { tableData, chartData };
};
