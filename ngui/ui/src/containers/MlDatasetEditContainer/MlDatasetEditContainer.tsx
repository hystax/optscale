import { useNavigate, useParams } from "react-router-dom";
import MlDatasetEdit from "components/MlDatasetEdit";
import MlDatasetService from "services/MlDatasetsService";

import { ML_DATASETS } from "urls";

const MlDatasetEditContainer = () => {
  const navigate = useNavigate();
  const { datasetId } = useParams();

  const { useGet, useUpdate } = MlDatasetService();

  const { isLoading: isGetDatasetLoading, dataset } = useGet(datasetId);
  const { isLoading: isUpdateDatasetLoading, onUpdate } = useUpdate();

  const redirect = () => navigate(ML_DATASETS);

  const onSubmit = (formData) => {
    // Path cannot be patched
    const { path: _, ...payload } = formData;
    onUpdate(datasetId, payload).then(() => redirect());
  };

  const onCancel = () => redirect();

  return (
    <MlDatasetEdit
      dataset={dataset}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoadingProps={{
        isGetDatasetLoading,
        isUpdateDatasetLoading
      }}
    />
  );
};

export default MlDatasetEditContainer;
