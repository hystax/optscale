import SummaryGrid from "components/SummaryGrid";
import { SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";

const Summary = ({ runsCount, lastRunsetExpenses, totalExpenses, isLoading }) => (
  <SummaryGrid
    summaryData={[
      {
        key: "runs",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: () => runsCount,
        color: "primary",
        captionMessageId: "runs",
        dataTestIds: {
          cardTestId: "card_runs"
        },
        isLoading
      },
      {
        key: "lastRunExpenses",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
        valueComponentProps: {
          value: lastRunsetExpenses
        },
        color: "primary",
        captionMessageId: "lastRunsetExpenses",
        dataTestIds: {
          cardTestId: "card_last_run_expenses"
        },
        isLoading
      },
      {
        key: "totalExpenses",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
        valueComponentProps: {
          value: totalExpenses
        },
        color: "primary",
        captionMessageId: "totalExpenses",
        dataTestIds: {
          cardTestId: "card_last_total_expenses"
        },
        isLoading
      }
    ]}
  />
);

export default Summary;
