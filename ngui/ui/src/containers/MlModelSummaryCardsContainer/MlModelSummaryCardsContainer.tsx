import { useParams } from "react-router-dom";
import ModelSummaryGrid from "components/MlModelDetails/ModelSummaryGrid";
import MlModelsService from "services/MlModelsService";

const MlModelSummaryCardsContainer = ({ model, isModelDetailsLoading }) => {
  const { taskId } = useParams();

  const { useGetModelRecommendations } = MlModelsService();
  const { isLoading: isGetRecommendationsLoading, recommendations } = useGetModelRecommendations(taskId);

  return (
    <ModelSummaryGrid
      model={model}
      recommendations={recommendations}
      isModelDetailsLoading={isModelDetailsLoading}
      isGetRecommendationsLoading={isGetRecommendationsLoading}
    />
  );
};

export default MlModelSummaryCardsContainer;
