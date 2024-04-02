import { useParams } from "react-router-dom";
import ExecutionBreakdown, { ExecutionBreakdownLoader } from "components/ExecutionBreakdown";
import MlTasksService from "services/MlTasksService";
import { getData } from "./utils";

const ExecutionBreakdownContainer = ({ reachedGoals, ...rest }) => {
  const { useGetRunBreakdown, useGetTaskRun } = MlTasksService();

  const { taskId, runId } = useParams();

  const {
    isLoading: isGetRunBreakdownLoading,
    isDataReady: isGetRunBreakdownDataReady,
    breakdown = {},
    milestones = [],
    stages = []
  } = useGetRunBreakdown(runId);

  const { isLoading: isTaskRunLoading, isDataReady: isTaskRunDataReady } = useGetTaskRun(runId);

  return isGetRunBreakdownLoading || !isGetRunBreakdownDataReady || isTaskRunLoading || !isTaskRunDataReady ? (
    <ExecutionBreakdownLoader />
  ) : (
    <ExecutionBreakdown {...getData({ breakdown, milestones, stages })} reachedGoals={reachedGoals} taskId={taskId} {...rest} />
  );
};

export default ExecutionBreakdownContainer;
