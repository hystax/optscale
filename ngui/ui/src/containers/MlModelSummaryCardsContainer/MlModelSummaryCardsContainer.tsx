import { useParams } from "react-router-dom";
import ModelSummaryGrid from "components/MlModelDetails/ModelSummaryGrid";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";
import { modelRecommendations } from "utils/mlDemoData/mlRecommendations";

const DemoContainer = ({ model, isModelDetailsLoading }) => (
  <ModelSummaryGrid
    model={model}
    recommendations={modelRecommendations}
    isModelDetailsLoading={isModelDetailsLoading}
    isGetRecommendationsLoading={false}
  />
);

const Container = ({ model, isModelDetailsLoading }) => {
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

const MlModelSummaryCardsContainer = ({ model, isModelDetailsLoading }) => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? (
    <DemoContainer model={model} isModelDetailsLoading={isModelDetailsLoading} />
  ) : (
    <Container model={model} isModelDetailsLoading={isModelDetailsLoading} />
  );
};

export default MlModelSummaryCardsContainer;
