import { useParams } from "react-router-dom";
import MlModelDetails from "components/MlModelDetails";
import MlModelsService from "services/MlModelsService";

const MlModelDetailsContainer = () => {
  const { taskId } = useParams();

  const { useGetOne } = MlModelsService();

  const { model, isLoading, isDataReady } = useGetOne(taskId);

  return <MlModelDetails isDataReady={isDataReady} isLoading={isLoading} model={model} />;
};

export default MlModelDetailsContainer;
