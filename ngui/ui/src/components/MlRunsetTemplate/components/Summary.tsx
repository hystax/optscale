import SummaryGrid from "components/SummaryGrid";
import { useIsOptScaleCapabilityEnabled } from "hooks/useIsOptScaleCapabilityEnabled";
import { OPTSCALE_CAPABILITY, SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";

type SummaryProps = {
  runsCount: number;
  lastRunsetExpenses: number;
  totalExpenses: number;
  isLoading?: boolean;
};

const Summary = ({ runsCount, lastRunsetExpenses, totalExpenses, isLoading = false }: SummaryProps) => {
  const isFinOpsEnabled = useIsOptScaleCapabilityEnabled(OPTSCALE_CAPABILITY.FINOPS);

  return (
    <SummaryGrid
      summaryData={[
        {
          key: "runs",
          valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
          CustomValueComponent: () => runsCount,
          color: "primary",
          captionMessageId: "runs",
          dataTestIds: {
            cardTestId: "card_runs",
          },
          isLoading,
        },
        ...(isFinOpsEnabled
          ? [
              {
                key: "lastRunsetExpenses",
                valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
                valueComponentProps: {
                  value: lastRunsetExpenses,
                },
                color: "primary",
                captionMessageId: "lastRunsetExpenses",
                dataTestIds: {
                  cardTestId: "card_last_run_expenses",
                },
                isLoading,
              },
              {
                key: "totalExpenses",
                valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
                valueComponentProps: {
                  value: totalExpenses,
                },
                color: "primary",
                captionMessageId: "totalExpenses",
                dataTestIds: {
                  cardTestId: "card_last_total_expenses",
                },
                isLoading,
              },
            ]
          : []),
      ]}
    />
  );
};

export default Summary;
