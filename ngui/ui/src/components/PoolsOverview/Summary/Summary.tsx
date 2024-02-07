import SummaryGrid from "components/SummaryGrid";
import { getPoolIdWithSubPools, getResourcesExpensesUrl } from "urls";
import { AVAILABLE_SAVINGS_FILTER, POOL_ID_FILTER, SUMMARY_CARD_TYPES, SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";
import { getCurrentMonthRange } from "utils/datetime";
import { getPoolColorStatus } from "utils/layouts";
import { intPercentXofY } from "utils/math";

type SummaryProps = {
  data: {
    id: string;
    limit: number;
    cost: number;
    forecast: number;
    saving: number;
    children: SummaryProps["data"][];
  };
  isLoading?: boolean;
};

const Summary = ({ data, isLoading = false }: SummaryProps) => {
  const { id, limit = 0, cost = 0, forecast = 0, saving = 0 } = data;

  const costPercent = intPercentXofY(cost, limit);
  const forecastPercent = intPercentXofY(forecast, limit);
  const { today, startOfMonth } = getCurrentMonthRange(true);

  const { exceededPools, exceededByValue } = [data, ...(data.children ?? [])].reduce(
    (acc, { limit: poolLimit, cost: poolExpenses }) => {
      if (poolExpenses > poolLimit && poolLimit !== 0) {
        return {
          exceededPools: acc.exceededPools + 1,
          exceededByValue: acc.exceededByValue + (poolExpenses - poolLimit)
        };
      }
      return acc;
    },
    { exceededPools: 0, exceededByValue: 0 }
  );

  const summaryDefinition = [
    {
      key: "totalExpensesMonthToDate",
      type: SUMMARY_CARD_TYPES.EXTENDED,
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: exceededByValue
      },
      captionMessageId: "spentOverLimit",
      relativeValue: exceededPools,
      relativeValueCaptionMessageId: "exceededLimit",
      dataTestIds: {
        cardTestId: "card_total_exp"
      },
      color: "error",
      renderCondition: () => !!exceededPools,
      isLoading
    },
    {
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: limit
      },
      captionMessageId: "organizationLimit",
      key: "pool",
      isLoading,
      dataTestIds: {
        cardTestId: "card_pool"
      }
    },
    {
      key: "expensesThisMonth",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: cost
      },
      color: getPoolColorStatus(costPercent),
      captionMessageId: "expensesThisMonth",
      isLoading,
      dataTestIds: {
        cardTestId: "card_expenses"
      }
    },
    {
      key: "forecastThisMonth",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: forecast
      },
      captionMessageId: "forecastThisMonth",
      color: getPoolColorStatus(forecastPercent),
      isLoading,
      dataTestIds: {
        cardTestId: "card_forecast"
      }
    },
    {
      key: "possibleMonthlySavings",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: saving
      },
      captionMessageId: "possibleMonthlySavings",
      renderCondition: () => saving !== 0,
      button: {
        show: true,
        link: getResourcesExpensesUrl({
          [POOL_ID_FILTER]: getPoolIdWithSubPools(id),
          [AVAILABLE_SAVINGS_FILTER]: true,
          sStartDate: startOfMonth,
          sEndDate: today
        }),
        tooltip: {
          show: true,
          messageId: "goToResources",
          placement: "top"
        }
      },
      isLoading,
      dataTestIds: {
        cardTestId: "card_savings"
      }
    }
  ];

  return <SummaryGrid summaryData={summaryDefinition} />;
};

export default Summary;
