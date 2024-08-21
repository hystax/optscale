import { useMemo } from "react";
import MlTasksService from "services/MlTasksService";
import RunsTab from "./RunsTab";

const RunsTabContainer = ({ taskId, candidateDetails, qualifiedRunIds, otherDatasetRunIds }) => {
  const runIds = useMemo(() => [...qualifiedRunIds, ...otherDatasetRunIds], [otherDatasetRunIds, qualifiedRunIds]);

  const { useGetTaskRunsBulk } = MlTasksService();

  const { isLoading, runs } = useGetTaskRunsBulk(taskId, runIds);

  const qualifiedRuns = runs.filter(({ id }) => qualifiedRunIds.includes(id));
  const otherDatasetRuns = runs.filter(({ id }) => otherDatasetRunIds.includes(id));

  const [primaryMetricKey, { name: primaryMetricName, func: primaryMetricAggregationFunction } = {}] =
    Object.entries(candidateDetails.primary_metric ?? {})[0] ?? [];

  const candidatePrimaryMetric = {
    key: primaryMetricKey,
    name: primaryMetricName,
    aggregateFunction: primaryMetricAggregationFunction
  };

  const candidateSecondaryMetrics = Object.entries(candidateDetails.metrics ?? {}).map(([key, payload]) => ({
    key,
    name: payload.name,
    aggregateFunction: payload.func
  }));

  return (
    <RunsTab
      candidatePrimaryMetric={candidatePrimaryMetric}
      candidateSecondaryMetrics={candidateSecondaryMetrics}
      qualifiedRuns={qualifiedRuns}
      otherDatasetRuns={otherDatasetRuns}
      isLoading={isLoading}
    />
  );
};

export default RunsTabContainer;
