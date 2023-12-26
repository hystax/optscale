import { useParams } from "react-router-dom";
import ExecutionBreakdown, { ExecutionBreakdownLoader } from "components/ExecutionBreakdown";
import MlModelsService from "services/MlModelsService";
import { getData } from "./utils";

const ExecutionBreakdownContainer = ({ reachedGoals, ...rest }) => {
  const { useGetRunBreakdown, useGetModelRun } = MlModelsService();

  const { taskId, runId } = useParams();

  const {
    isLoading: isGetRunBreakdownLoading,
    isDataReady: isGetRunBreakdownDataReady,
    breakdown = {},
    milestones = [],
    stages = []
  } = useGetRunBreakdown(runId);

  const { isLoading: isModelRunLoading, isDataReady: isModelRunDataReady } = useGetModelRun(runId);

  return isGetRunBreakdownLoading || !isGetRunBreakdownDataReady || isModelRunLoading || !isModelRunDataReady ? (
    <ExecutionBreakdownLoader />
  ) : (
    <ExecutionBreakdown {...getData({ breakdown, milestones, stages })} reachedGoals={reachedGoals} taskId={taskId} {...rest} />
  );
};

export default ExecutionBreakdownContainer;
