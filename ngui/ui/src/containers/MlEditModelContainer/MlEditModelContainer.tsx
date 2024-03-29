import MlEditModel from "components/MlEditModel";
import MlModelsService from "services/MlModelsService";

type MlEditModelContainerProps = {
  modelId: string;
};

const MlEditModelContainer = ({ modelId }: MlEditModelContainerProps) => {
  const { useGet } = MlModelsService();
  const { isLoading, model } = useGet(modelId);

  return <MlEditModel model={model} isLoading={isLoading} />;
};

export default MlEditModelContainer;
