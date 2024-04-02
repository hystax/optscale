import { useMemo } from "react";
import { Box } from "@mui/material";
import { useNavigate, useParams } from "react-router-dom";
import SetupLeaderboardsForm, { FIELD_NAMES } from "components/SetupLeaderboardsForm";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import MlTasksService from "services/MlTasksService";
import { getMlTaskDetailsUrl } from "urls";
import { ML_TASK_DETAILS_TAB_NAME } from "utils/constants";
import { getQueryParams } from "utils/network";
import { isEmpty as isEmptyObject } from "utils/objects";

const MlEditTaskLeaderboardContainer = ({ leaderboard, task }) => {
  const navigate = useNavigate();

  const { taskId } = useParams();

  const { metrics = [] } = task;

  const { useGetTaskRunsList } = MlTasksService();
  const { isLoading: isGetRunsListLoading, runs } = useGetTaskRunsList(taskId);

  const { useUpdateLeaderboard, useCreateLeaderboard } = MlLeaderboardsService();
  const { isLoading: isUpdateLeaderboardLoading, onUpdate } = useUpdateLeaderboard();
  const { isLoading: isCreateLeaderboardLoading, onCreate } = useCreateLeaderboard();

  const runTags = useMemo(() => Array.from(new Set(runs.flatMap((run) => Object.keys(run.tags)))), [runs]);

  const defaultValues = useMemo(
    () => ({
      [FIELD_NAMES.RUN_TAGS_FIELD_NAME]: leaderboard.grouping_tags ?? [],
      [FIELD_NAMES.GROUP_BY_HYPERPARAMETERS_FIELD_NAME]: leaderboard.group_by_hp ?? false,
      [FIELD_NAMES.PRIMARY_METRIC_FIELD_NAME]: leaderboard?.primary_metric
        ? {
            id: leaderboard.primary_metric?.id,
            name: leaderboard.primary_metric?.name
          }
        : null,
      [FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME]:
        leaderboard.other_metrics?.map(({ id, name }) => ({
          id,
          name
        })) ?? [],
      [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.NAME]:
        leaderboard.filters
          ?.map(({ max, min, id }) => ({
            [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC_MIN]: min ?? "",
            [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC_MAX]: max ?? "",
            [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC]: id
          }))
          .filter(Boolean) ?? []
    }),
    [
      leaderboard.filters,
      leaderboard.group_by_hp,
      leaderboard.grouping_tags,
      leaderboard.other_metrics,
      leaderboard.primary_metric
    ]
  );

  const redirectToTaskDetails = () => {
    const { [ML_TASK_DETAILS_TAB_NAME]: taskDetailsTab } = getQueryParams();

    return navigate(`${getMlTaskDetailsUrl(taskId)}?${ML_TASK_DETAILS_TAB_NAME}=${taskDetailsTab}`);
  };

  return (
    <Box
      sx={{
        width: { md: "50%" }
      }}
    >
      <SetupLeaderboardsForm
        metrics={metrics}
        runTags={runTags}
        defaultValues={defaultValues}
        isLoadingProps={{
          isGetDataLoading: isGetRunsListLoading,
          isSubmitDataLoading: isUpdateLeaderboardLoading || isCreateLeaderboardLoading
        }}
        onSubmit={(formData) => {
          const params = {
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
            other_metrics: formData[FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME].map(({ id }) => id),
            primary_metric: formData[FIELD_NAMES.PRIMARY_METRIC_FIELD_NAME].id
          };

          const apiHandler = isEmptyObject(leaderboard) ? onCreate : onUpdate;
          apiHandler(taskId, params).then(redirectToTaskDetails);
        }}
        onCancel={redirectToTaskDetails}
      />
    </Box>
  );
};

export default MlEditTaskLeaderboardContainer;
