import { useMemo } from "react";
import { useParams } from "react-router-dom";
import ExecutionBreakdown, { ExecutionBreakdownLoader } from "components/ExecutionBreakdown";
import MlTasksService from "services/MlTasksService";
import { getData } from "./utils";

const Charts = ({
  run,
  organizationId,
  arceeToken,
  isPublicRun = false,
  isTaskRunLoading = false,
  isTaskRunDataReady = false,
}) => {
  const { useGetRunBreakdown } = MlTasksService();

  const { runId } = useParams();

  const runBreakdownParams = useMemo(
    () => ({
      arceeToken,
    }),
    [arceeToken]
  );

  const {
    isLoading: isGetRunBreakdownLoading,
    isDataReady: isGetRunBreakdownDataReady,
    breakdown: apiBreakdown = {},
    milestones: apiMilestones = [],
    stages: apiStages = [],
  } = useGetRunBreakdown(organizationId, runId, runBreakdownParams);

  if (isGetRunBreakdownLoading || !isGetRunBreakdownDataReady || isTaskRunLoading || !isTaskRunDataReady) {
    return <ExecutionBreakdownLoader />;
  }

  const { breakdown, milestones, stages } = getData({ breakdown: apiBreakdown, milestones: apiMilestones, stages: apiStages });

  const { reached_goals: reachedGoals = [], task: { id: taskId } = {} } = run;

  return (
    <ExecutionBreakdown
      organizationId={organizationId}
      arceeToken={arceeToken}
      isPublicRun={isPublicRun}
      breakdown={breakdown}
      milestones={milestones}
      stages={stages}
      reachedGoals={reachedGoals}
      taskId={taskId}
    />
  );
};

export default Charts;
