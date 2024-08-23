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

const MlEditTaskLeaderboardTemplateContainer = ({ leaderboardTemplate, task }) => {
  const navigate = useNavigate();

  const { taskId } = useParams();

  const { metrics = [] } = task;

  const { useGetTaskTags } = MlTasksService();
  const { isLoading: isGetTaskTagsLoading, tags } = useGetTaskTags(taskId);

  const { useGetLabels: useGetDatasetLabels } = MlDatasetsService();
  const { isLoading: isGetDatasetLabelsLoading, labels: datasetLabels } = useGetDatasetLabels();

  const { useUpdateLeaderboardTemplate, useCreateLeaderboardTemplate } = MlLeaderboardsService();
  const { isLoading: isUpdateLeaderboardTemplateLoading, onUpdate } = useUpdateLeaderboardTemplate();
  const { isLoading: isCreateLeaderboardTemplateLoading, onCreate } = useCreateLeaderboardTemplate();

  const defaultValues = useMemo(
    () =>
      getDefaultValues({
        tags: leaderboardTemplate.grouping_tags,
        groupByHyperparameters: leaderboardTemplate.group_by_hp,
        primaryMetric: leaderboardTemplate.primary_metric,
        secondaryMetrics: leaderboardTemplate.other_metrics,
        metricRestrictions: leaderboardTemplate.filters,
        datasetCoverageRules: leaderboardTemplate.dataset_coverage_rules
      }),
    [
      leaderboardTemplate.dataset_coverage_rules,
      leaderboardTemplate.filters,
      leaderboardTemplate.group_by_hp,
      leaderboardTemplate.grouping_tags,
      leaderboardTemplate.other_metrics,
      leaderboardTemplate.primary_metric
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
          const apiHandler = isEmptyObject(leaderboardTemplate) ? onCreate : onUpdate;
          apiHandler(taskId, formData).then(redirectToTaskDetails);
        }}
        onCancel={redirectToTaskDetails}
        groupingTags={tags}
        metrics={metrics}
        datasetLabels={datasetLabels}
        isTemplate
        isLoadingProps={{
          isGetDataLoading: isGetTaskTagsLoading || isGetDatasetLabelsLoading,
          isSubmitDataLoading: isUpdateLeaderboardTemplateLoading || isCreateLeaderboardTemplateLoading
        }}
      />
    </Box>
  );
};

export default MlEditTaskLeaderboardTemplateContainer;
