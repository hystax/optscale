import { useParams } from "react-router-dom";
import MlModelRunsList from "components/MlModelRunsList";
import MlModelsService from "services/MlModelsService";

const MlModelRunsListContainer = () => {
  const { modelId } = useParams();

  const { useGetModelRunsList } = MlModelsService();
  const { runs = [], isLoading, isDataReady } = useGetModelRunsList(modelId);

  return <MlModelRunsList runs={runs} isLoading={isLoading || !isDataReady} />;
};

export default MlModelRunsListContainer;
