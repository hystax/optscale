import { useMemo } from "react";
import { intl } from "translations/react-intl-config";
import { AWS_CNR, AZURE_CNR, ALIBABA_CNR, NOT_SET_CLOUD_TYPE } from "utils/constants";
import { formatISO } from "utils/datetime";

const LINE_ITEM_DESCRIPTION = "lineItem/LineItemDescription";
const LINE_ITEM_BLENDED_RATE = "lineItem/BlendedRate";

const BILLING_ITEM = "BillingItem";

const PRICING_UNIT = "pricing/unit";

const getCloudType = (item = {}) => {
  if (item[LINE_ITEM_DESCRIPTION]) {
    return AWS_CNR;
  }
  if (item.meter_details?.meter_name) {
    return AZURE_CNR;
  }
  if (item[BILLING_ITEM]) {
    return ALIBABA_CNR;
  }
  return NOT_SET_CLOUD_TYPE;
};

const expensesCategoryNameGetterFactory = (cloudType) => {
  const getAwsExpenseCategoryName = (item) => item?.[LINE_ITEM_DESCRIPTION];
  const getAzureExpenseCategoryName = (item) => item?.meter_details?.meter_name;
  const getAlibabaExpenseCategoryName = (item) => item?.[BILLING_ITEM];
  const getDefaultExpenseCategoryName = () => intl.formatMessage({ id: "totalExpenses" });

  return {
    [AWS_CNR]: getAwsExpenseCategoryName,
    [AZURE_CNR]: getAzureExpenseCategoryName,
    [ALIBABA_CNR]: getAlibabaExpenseCategoryName,
    // If we could not identify cloud_type by the raw_data -> place it in the default group - "Total expenses"
    [NOT_SET_CLOUD_TYPE]: getDefaultExpenseCategoryName
  }[cloudType];
};

const getExpensesCategoryName = (item) => {
  const cloudType = getCloudType(item);
  const getCategoryName = expensesCategoryNameGetterFactory(cloudType);
  return getCategoryName(item);
};

const cloudTypeDependentDataObjectGetterFactory = (cloudType) => {
  if (cloudType === AWS_CNR) {
    return (item) => {
      const lineItemBlendedRate = +item[LINE_ITEM_BLENDED_RATE];
      const pricingUnit = item[PRICING_UNIT];
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
    };
  }
  return () => {};
};

const getDataObject = (item) => {
  const cloudType = getCloudType(item);
  const getCloudTypeDependentDataObject = cloudTypeDependentDataObjectGetterFactory(cloudType);

  return {
    date: formatISO(item.start_date),
    expense: item.cost ?? 0,
    cloudType,
    ...getCloudTypeDependentDataObject(item)
  };
};

export const useResourceRawExpensesGroupedData = ({ expenses }) =>
  useMemo(
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
    () =>
      expenses.reduce((result, item) => {
        const expensesCategoryName = getExpensesCategoryName(item);

        return {
          ...result,
          [expensesCategoryName]: [...(result[expensesCategoryName] ?? []), getDataObject(item)]
        };
      }, {}),

    [expenses]
  );
