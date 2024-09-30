import SummaryGrid from "components/SummaryGrid";
import SummaryService from "services/SummaryService";
import { RECOMMENDATIONS } from "urls";
import { SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";

const ExpensesSummaryContainer = ({ requestParams }) => {
  const { useGet } = SummaryService();
  const { isLoading, data } = useGet({ params: requestParams });
  const { total_saving: totalSaving = 0, total_cost: totalExpenses = 0, total_count: totalCount } = data;

  const summaryData = [
    {
      key: "totalExpenses",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalExpenses
      },
      captionMessageId: "totalExpenses",
      isLoading,
      dataTestIds: {
        cardTestId: "card_total_expenses",
        titleTestId: "p_expenses",
        valueTestId: "p_expenses_value"
      }
    },
    {
      key: "totalCount",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
      valueComponentProps: {
        value: totalCount
      },
      captionMessageId: "resourceCount",
      isLoading,
      dataTestIds: {
        cardTestId: "card_total_count",
        titleTestId: "p_count",
        valueTestId: "p_count_value"
      }
    },
    {
      key: "possibleMonthlySavings",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalSaving
      },
      captionMessageId: "possibleMonthlySavings",
      renderCondition: () => totalSaving !== 0,
      isLoading,
      button: {
        show: true,
        link: RECOMMENDATIONS,
        tooltip: {
          show: true,
          messageId: "seeAllRecommendations",
          placement: "top"
        }
      },
      dataTestIds: {
        cardTestId: "card_possible_savings",
        titleTestId: "p_savings",
        valueTestId: "p_savings_value"
      }
    }
  ];

  return <SummaryGrid summaryData={summaryData} />;
};

export default ExpensesSummaryContainer;
