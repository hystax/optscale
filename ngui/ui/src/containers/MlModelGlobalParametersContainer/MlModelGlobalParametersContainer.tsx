import MlModelGlobalParameters from "components/MlModelGlobalParameters";
import MlModelsService from "services/MlModelsService";

const MlModelGlobalParametersContainer = () => {
  const { useGetGlobalParameters } = MlModelsService();

  const { isLoading, parameters } = useGetGlobalParameters();

  return <MlModelGlobalParameters parameters={parameters} isLoading={isLoading} />;
};

export default MlModelGlobalParametersContainer;
