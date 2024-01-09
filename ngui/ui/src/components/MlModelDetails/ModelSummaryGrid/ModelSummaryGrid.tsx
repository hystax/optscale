import FormattedDuration from "components/FormattedDuration";
import MlModelStatus from "components/MlModelStatus";
import SummaryGrid from "components/SummaryGrid";
import { ML_MODEL_STATUS, SUMMARY_CARD_TYPES, SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";

const ModelSummaryGrid = ({ model, recommendations, isGetRecommendationsLoading, isModelDetailsLoading }) => {
  const { status, last_run_duration: lastRunDuration, total_cost: totalCost = 0 } = model;
  const { total_count: recommendationsCount, total_saving: totalSaving } = recommendations;

  const items = [
    {
      key: "status",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
      CustomValueComponent: MlModelStatus,
      valueComponentProps: { status, iconSize: "medium" },
      color: {
        [ML_MODEL_STATUS.CREATED]: "info",
        [ML_MODEL_STATUS.RUNNING]: "primary",
        [ML_MODEL_STATUS.ABORTED]: "info",
        [ML_MODEL_STATUS.COMPLETED]: "success",
        [ML_MODEL_STATUS.FAILED]: "error"
      }[status],
      captionMessageId: "status",
      renderCondition: () => status !== undefined,
      isLoading: isModelDetailsLoading,
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
        cardTestId: "card_last_model_duration"
      },
      isLoading: isModelDetailsLoading
    },
    {
      key: "lifetimeCost",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalCost
      },
      captionMessageId: "lifetimeCost",
      isLoading: isModelDetailsLoading
    },
    {
      key: "recommendations",
      type: SUMMARY_CARD_TYPES.EXTENDED,
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalSaving
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
      isLoading: isGetRecommendationsLoading
    }
  ];

  return <SummaryGrid summaryData={items} />;
};

export default ModelSummaryGrid;
