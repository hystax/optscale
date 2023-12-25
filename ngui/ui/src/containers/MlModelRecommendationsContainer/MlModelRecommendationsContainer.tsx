import { useParams } from "react-router-dom";
import MlModelRecommendations from "components/MlModelRecommendations";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";

const DemoContainer = () => {
  const { taskId } = useParams();

  return <MlModelRecommendations taskId={taskId} isLoading={false} recommendations={MlModelRecommendations} />;
};

const Container = () => {
  const { taskId } = useParams();

  const { useGetModelRecommendations } = MlModelsService();
  const { isLoading: isGetRecommendationsLoading, recommendations } = useGetModelRecommendations(taskId);
  return <MlModelRecommendations taskId={taskId} isLoading={isGetRecommendationsLoading} recommendations={recommendations} />;
};

const MlModelRecommendationsContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlModelRecommendationsContainer;
