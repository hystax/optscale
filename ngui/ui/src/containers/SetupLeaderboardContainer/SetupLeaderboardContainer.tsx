import { useNavigate, useParams } from "react-router-dom";
import SetupLeaderboard from "components/SetupLeaderboard";
import { FIELD_NAMES } from "components/SetupLeaderboardsForm";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import MlTasksService from "services/MlTasksService";
import { getMlTaskDetailsUrl } from "urls";

const SetupLeaderboardContainer = () => {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const mlTaskDetailsUrl = getMlTaskDetailsUrl(taskId);

  const { useGetOne, useGetTaskRunsList } = MlTasksService();

  const { isLoading: isGetTaskLoading, task } = useGetOne(taskId);
  const { isLoading: isGetRunsListLoading, runs } = useGetTaskRunsList(taskId);

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
              max: max ? Number(max) : undefined,
              min: min ? Number(min) : undefined
            })
          ),
          group_by_hp: formData[FIELD_NAMES.GROUP_BY_HYPERPARAMETERS_FIELD_NAME],
          grouping_tags: formData[FIELD_NAMES.RUN_TAGS_FIELD_NAME],
          other_metrics: formData[FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME].map(({ id }) => id),
          primary_metric: formData[FIELD_NAMES.PRIMARY_METRIC_FIELD_NAME].id
        }).then(() => navigate(mlTaskDetailsUrl));
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
