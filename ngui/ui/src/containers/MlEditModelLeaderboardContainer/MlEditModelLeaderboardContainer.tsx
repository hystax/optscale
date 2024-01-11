import { useMemo } from "react";
import { Box } from "@mui/material";
import { useNavigate, useParams } from "react-router-dom";
import SetupLeaderboardsForm, { FIELD_NAMES } from "components/SetupLeaderboardsForm";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import MlModelsService from "services/MlModelsService";
import { getMlModelDetailsUrl } from "urls";
import { ML_MODEL_DETAILS_TAB_NAME } from "utils/constants";
import { getQueryParams } from "utils/network";
import { isEmpty as isEmptyObject } from "utils/objects";

const MlEditModelParametersContainer = ({ leaderboard, task }) => {
  const navigate = useNavigate();

  const { taskId } = useParams();

  const { goals: metrics = [] } = task;

  const { useGetModelRunsList } = MlModelsService();
  const { isLoading: isGetRunsListLoading, runs } = useGetModelRunsList(taskId);

  const { useUpdateLeaderboard, useCreateLeaderboard } = MlLeaderboardsService();
  const { isLoading: isUpdateLeaderboardLoading, onUpdate } = useUpdateLeaderboard();
  const { isLoading: isCreateLeaderboardLoading, onCreate } = useCreateLeaderboard();

  const runTags = useMemo(() => Array.from(new Set(runs.flatMap((run) => Object.keys(run.tags)))), [runs]);

  const defaultValues = useMemo(
    () => ({
      [FIELD_NAMES.RUN_TAGS_FIELD_NAME]: leaderboard.grouping_tags ?? [],
      [FIELD_NAMES.GROUP_BY_HYPERPARAMETERS_FIELD_NAME]: leaderboard.group_by_hp ?? false,
      [FIELD_NAMES.PRIMARY_METRIC_FIELD_NAME]: leaderboard?.primary_goal
        ? {
            id: leaderboard.primary_goal?.id,
            name: leaderboard.primary_goal?.name
          }
        : null,
      [FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME]:
        leaderboard.other_goals?.map(({ id, name }) => ({
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
    [leaderboard.filters, leaderboard.group_by_hp, leaderboard.grouping_tags, leaderboard.other_goals, leaderboard.primary_goal]
  );

  const redirectToModelDetails = () => {
    const { [ML_MODEL_DETAILS_TAB_NAME]: taskDetailsTab } = getQueryParams();

    return navigate(`${getMlModelDetailsUrl(taskId)}?${ML_MODEL_DETAILS_TAB_NAME}=${taskDetailsTab}`);
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
            other_goals: formData[FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME].map(({ id }) => id),
            primary_goal: formData[FIELD_NAMES.PRIMARY_METRIC_FIELD_NAME].id
          };

          const apiHandler = isEmptyObject(leaderboard) ? onCreate : onUpdate;
          apiHandler(taskId, params).then(redirectToModelDetails);
        }}
        onCancel={redirectToModelDetails}
      />
    </Box>
  );
};

export default MlEditModelParametersContainer;
