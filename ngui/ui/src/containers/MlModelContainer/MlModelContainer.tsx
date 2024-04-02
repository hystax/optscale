import MlModel from "components/MlModel";
import MlModelsService from "services/MlModelsService";

type MlModelContainerProps = {
  modelId: string;
};

const MlModelContainer = ({ modelId }: MlModelContainerProps) => {
  const { useGet } = MlModelsService();
  const { isLoading, model } = useGet(modelId);

  return <MlModel model={model} isLoading={isLoading} />;
};

export default MlModelContainer;
