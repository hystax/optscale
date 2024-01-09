import MlDatasets from "components/MlDatasets";
import MlDatasetsService from "services/MlDatasetsService";

const MlDatasetsContainer = () => {
  const { useGetAll } = MlDatasetsService();

  const { isLoading, datasets } = useGetAll();

  return <MlDatasets datasets={datasets} isLoading={isLoading} />;
};

export default MlDatasetsContainer;
