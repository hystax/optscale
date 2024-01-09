import { useMemo } from "react";
import LeaderboardDatasetForm, { FIELD_NAMES } from "components/LeaderboardDatasetForm";
import MlDatasetsService from "services/MlDatasetsService";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const EditLeaderboardDatasetFormContainer = ({ leaderboardDataset, onSuccess, onCancel }) => {
  const { useGetAll } = MlDatasetsService();
  const { isLoading: isDatasetsLoading, datasets } = useGetAll();

  const { useUpdateLeaderboardDataset } = MlLeaderboardsService();
  const { isLoading: isUpdateLeaderboardDatasetLoading, onUpdate } = useUpdateLeaderboardDataset();

  const defaultValues = useMemo(
    () => ({
      [FIELD_NAMES.NAME]: leaderboardDataset.name,
      [FIELD_NAMES.SELECTED_DATASETS]: datasets.filter(({ id }) => leaderboardDataset.dataset_ids.includes(id))
    }),
    [datasets, leaderboardDataset.dataset_ids, leaderboardDataset.name]
  );

  return (
    <LeaderboardDatasetForm
      onSubmit={(formData) =>
        onUpdate(leaderboardDataset.id, {
          name: formData[FIELD_NAMES.NAME],
          datasetIds: formData[FIELD_NAMES.SELECTED_DATASETS].map(({ id }) => id)
        }).then(onSuccess)
      }
      onCancel={onCancel}
      datasets={datasets}
      defaultValues={defaultValues}
      isLoadingProps={{
        isGetDataLoading: isDatasetsLoading,
        isSubmitDataLoading: isUpdateLeaderboardDatasetLoading
      }}
    />
  );
};

export default EditLeaderboardDatasetFormContainer;
