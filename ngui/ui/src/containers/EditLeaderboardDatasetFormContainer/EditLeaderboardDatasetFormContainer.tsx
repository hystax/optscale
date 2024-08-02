import { useMemo } from "react";
import LeaderboardForm from "components/LeaderboardForm";
import { getDefaultValues } from "components/LeaderboardForm/utils";
import { useLeaderboardDatasetFormContainerData } from "hooks/useLeaderboardDatasetFormContainerData";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const EditLeaderboardDatasetFormContainer = ({ task, leaderboardDataset, onSuccess, onCancel }) => {
  const {
    data: { datasets, datasetLabels, groupingTags },
    isLoading: isGetDataLoading
  } = useLeaderboardDatasetFormContainerData({
    taskId: task.id
  });

  const { useUpdateLeaderboardDataset } = MlLeaderboardsService();
  const { isLoading: isUpdateLeaderboardDatasetLoading, onUpdate } = useUpdateLeaderboardDataset();

  const defaultValues = useMemo(
    () =>
      getDefaultValues({
        name: leaderboardDataset.name,
        selectedDatasets: datasets.filter(({ id }) => leaderboardDataset.dataset_ids.includes(id)),
        tags: leaderboardDataset.grouping_tags,
        groupByHyperparameters: leaderboardDataset.group_by_hp,
        primaryMetric: leaderboardDataset.primary_metric,
        secondaryMetrics: leaderboardDataset.other_metrics,
        metricRestrictions: leaderboardDataset.filters,
        datasetCoverageRules: leaderboardDataset.dataset_coverage_rules
      }),
    [
      datasets,
      leaderboardDataset.dataset_coverage_rules,
      leaderboardDataset.dataset_ids,
      leaderboardDataset.filters,
      leaderboardDataset.group_by_hp,
      leaderboardDataset.grouping_tags,
      leaderboardDataset.name,
      leaderboardDataset.other_metrics,
      leaderboardDataset.primary_metric
    ]
  );

  return (
    <LeaderboardForm
      defaultValues={defaultValues}
      onSubmit={(submitData) => onUpdate(leaderboardDataset.id, submitData).then(onSuccess)}
      onCancel={onCancel}
      datasets={datasets}
      groupingTags={groupingTags}
      metrics={task.metrics}
      datasetLabels={datasetLabels}
      isLoadingProps={{
        isGetDataLoading,
        isSubmitDataLoading: isUpdateLeaderboardDatasetLoading
      }}
    />
  );
};

export default EditLeaderboardDatasetFormContainer;
