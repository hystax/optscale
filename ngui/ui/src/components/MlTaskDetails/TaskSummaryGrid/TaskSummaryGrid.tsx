import FormattedDuration from "components/FormattedDuration";
import MlTaskStatus from "components/MlTaskStatus";
import SummaryGrid from "components/SummaryGrid";
import { useIsOptScaleModeEnabled } from "hooks/useIsOptScaleModeEnabled";
import { ML_TASK_STATUS, OPTSCALE_MODE, SUMMARY_CARD_TYPES, SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";

const TaskSummaryGrid = ({ task, recommendations, isGetRecommendationsLoading, isTaskDetailsLoading }) => {
  const isFinOpsEnabled = useIsOptScaleModeEnabled(OPTSCALE_MODE.FINOPS);

  const { status, last_run_duration: lastRunDuration, total_cost: totalCost = 0 } = task;
  const { total_count: recommendationsCount, total_saving: totalSaving } = recommendations;

  const items = [
    {
      key: "status",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
      CustomValueComponent: MlTaskStatus,
      valueComponentProps: { status, iconSize: "medium" },
      color: {
        [ML_TASK_STATUS.CREATED]: "info",
        [ML_TASK_STATUS.RUNNING]: "primary",
        [ML_TASK_STATUS.ABORTED]: "info",
        [ML_TASK_STATUS.COMPLETED]: "success",
        [ML_TASK_STATUS.FAILED]: "error"
      }[status],
      captionMessageId: "status",
      renderCondition: () => status !== undefined,
      isLoading: isTaskDetailsLoading,
      dataTestIds: {
        cardTestId: "card_run_status"
      }
    },
    {
      key: "duration",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
      CustomValueComponent: FormattedDuration,
      valueComponentProps: {
        durationInSeconds: lastRunDuration
      },
      renderCondition: () => lastRunDuration && lastRunDuration !== 0,
      captionMessageId: "lastRunDuration",
      dataTestIds: {
        cardTestId: "card_last_task_duration"
      },
      isLoading: isTaskDetailsLoading
    },
    {
      key: "lifetimeCost",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalCost
      },
      captionMessageId: "lifetimeCost",
      isLoading: isTaskDetailsLoading,
      renderCondition: () => isFinOpsEnabled
    },
    {
      key: "recommendations",
      type: SUMMARY_CARD_TYPES.EXTENDED,
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalSaving
      },
      help: {
        show: true,
        messageId: "projectedMonthlySavingsForRelatedInfrastructure"
      },
      captionMessageId: "summarySavings",
      relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
      relativeValueComponentProps: {
        value: recommendationsCount
      },
      relativeValueCaptionMessageId: "recommendationsCount",
      dataTestIds: {
        cardTestId: "card_total_exp"
      },
      color: totalSaving || recommendationsCount > 20 ? "error" : "success",
      isLoading: isGetRecommendationsLoading,
      renderCondition: () => isFinOpsEnabled
    }
  ];

  return <SummaryGrid summaryData={items} />;
};

export default TaskSummaryGrid;
