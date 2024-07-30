import { useMemo } from "react";
import { Box } from "@mui/material";
import { useNavigate, useParams } from "react-router-dom";
import LeaderboardForm from "components/LeaderboardForm";
import { getDefaultValues } from "components/LeaderboardForm/utils";
import MlDatasetsService from "services/MlDatasetsService";
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

  const { useGetLabels: useGetDatasetLabels } = MlDatasetsService();
  const { isLoading: isGetDatasetLabelsLoading, labels: datasetLabels } = useGetDatasetLabels();

  const { useUpdateLeaderboard, useCreateLeaderboard } = MlLeaderboardsService();
  const { isLoading: isUpdateLeaderboardLoading, onUpdate } = useUpdateLeaderboard();
  const { isLoading: isCreateLeaderboardLoading, onCreate } = useCreateLeaderboard();

  const runTags = useMemo(() => Array.from(new Set(runs.flatMap((run) => Object.keys(run.tags)))), [runs]);

  const defaultValues = useMemo(
    () =>
      getDefaultValues({
        tags: leaderboard.grouping_tags,
        groupByHyperparameters: leaderboard.group_by_hp,
        primaryMetric: leaderboard.primary_metric,
        secondaryMetrics: leaderboard.other_metrics,
        metricRestrictions: leaderboard.filters,
        datasetCoverageRules: leaderboard.dataset_coverage_rules
      }),
    [
      leaderboard.dataset_coverage_rules,
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
      <LeaderboardForm
        defaultValues={defaultValues}
        onSubmit={(formData) => {
          const apiHandler = isEmptyObject(leaderboard) ? onCreate : onUpdate;
          apiHandler(taskId, formData).then(redirectToTaskDetails);
        }}
        onCancel={redirectToTaskDetails}
        runTags={runTags}
        metrics={metrics}
        datasetLabels={datasetLabels}
        isTemplate
        isLoadingProps={{
          isGetDataLoading: isGetRunsListLoading || isGetDatasetLabelsLoading,
          isSubmitDataLoading: isUpdateLeaderboardLoading || isCreateLeaderboardLoading
        }}
      />
    </Box>
  );
};

export default MlEditTaskLeaderboardContainer;
