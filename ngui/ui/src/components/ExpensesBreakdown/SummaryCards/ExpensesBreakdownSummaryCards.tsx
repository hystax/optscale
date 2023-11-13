import SummaryGrid from "components/SummaryGrid";
import { SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";
import { getPoolColorStatus } from "utils/layouts";
import { intPercentXofY } from "utils/math";

const ExpensesBreakdownSummaryCards = ({ total = 0, previousTotal = 0, isLoading = false, pdfIds = {} }) => {
  const percent = intPercentXofY(total, previousTotal);

  const summaryData = [
    {
      key: "totalExpensesForSelectedPeriod",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: total
      },
      color: getPoolColorStatus(percent),
      isLoading,
      captionMessageId: "totalExpensesForSelectedPeriod",
      pdfId: pdfIds.totalExpensesForSelectedPeriod
    },
    {
      key: "totalExpensesForPreviousPeriod",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: previousTotal
      },
      isLoading,
      captionMessageId: "totalExpensesForPreviousPeriod",
      pdfId: pdfIds.totalExpensesForPreviousPeriod
    }
  ];
  return <SummaryGrid summaryData={summaryData} />;
};

export default ExpensesBreakdownSummaryCards;
