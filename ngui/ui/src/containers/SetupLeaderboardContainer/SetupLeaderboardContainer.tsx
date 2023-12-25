import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import SetupLeaderboard from "components/SetupLeaderboard";
import { FIELD_NAMES } from "components/SetupLeaderboardsForm";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import MlModelsService from "services/MlModelsService";
import { getMlModelDetailsUrl } from "urls";

const SetupLeaderboardContainer = () => {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const mlModelDetailsUrl = getMlModelDetailsUrl(taskId);

  const { useGetOne, useGetModelRunsList } = MlModelsService();

  const { isLoading: isGetTaskLoading, model: task } = useGetOne(taskId);
  const { isLoading: isGetRunsListLoading, runs } = useGetModelRunsList(taskId);

  const { useCreateLeaderboard } = MlLeaderboardsService();
  const { isLoading: isCreateLeaderboardLoading, onCreate } = useCreateLeaderboard();

  return (
    <SetupLeaderboard
      onSetup={(formData) => {
        onCreate(taskId, {
          filters: formData[FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.NAME].map(
            ({
              [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC]: id,
              [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC_MAX]: max,
              [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC_MIN]: min
            }) => ({
              id,
              max,
              min
            })
          ),
          group_by_hp: formData[FIELD_NAMES.GROUP_BY_HYPERPARAMETERS_FIELD_NAME],
          grouping_tags: formData[FIELD_NAMES.RUN_TAGS_FIELD_NAME],
          other_goals: formData[FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME].map(({ id }) => id),
          primary_goal: formData[FIELD_NAMES.PRIMARY_METRIC_FIELD_NAME].id
        }).then(() => navigate(mlModelDetailsUrl));
      }}
      task={task}
      runs={runs}
      isLoadingProps={{
        isGetTaskLoading,
        isGetRunsListLoading,
        isSetupLoading: isCreateLeaderboardLoading
      }}
    />
  );
};

export default SetupLeaderboardContainer;
