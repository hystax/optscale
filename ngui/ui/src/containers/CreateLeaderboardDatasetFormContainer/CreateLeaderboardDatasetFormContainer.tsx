import React, { useMemo } from "react";
import LeaderboardDatasetForm, { FIELD_NAMES } from "components/LeaderboardDatasetForm";
import MlDatasetsService from "services/MlDatasetsService";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const CreateLeaderboardDatasetFormContainer = ({ leaderboardId, onSuccess, onCancel }) => {
  const { useGetAll } = MlDatasetsService();
  const { isLoading: isDatasetsLoading, datasets } = useGetAll();

  const { useCreateLeaderboardDataset } = MlLeaderboardsService();
  const { isLoading: isCreateLeaderboardDatasetLoading, onCreate } = useCreateLeaderboardDataset();

  const defaultValues = useMemo(
    () => ({
      [FIELD_NAMES.NAME]: "",
      [FIELD_NAMES.SELECTED_DATASETS]: []
    }),
    []
  );

  return (
    <LeaderboardDatasetForm
      onCancel={onCancel}
      onSubmit={(formData) => {
        onCreate(leaderboardId, {
          datasetIds: formData[FIELD_NAMES.SELECTED_DATASETS].map(({ id }) => id),
          name: formData[FIELD_NAMES.NAME]
        }).then(onSuccess);
      }}
      datasets={datasets}
      defaultValues={defaultValues}
      isLoadingProps={{
        isGetDataLoading: isDatasetsLoading,
        isSubmitDataLoading: isCreateLeaderboardDatasetLoading
      }}
    />
  );
};

export default CreateLeaderboardDatasetFormContainer;
