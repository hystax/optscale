import { useParams } from "react-router-dom";
import MlTaskRun from "components/MlTaskRun";
import MlTasksService from "services/MlTasksService";

const MlTaskRunContainer = () => {
  const { runId } = useParams();

  const { useGetTaskRun } = MlTasksService();

  const { isLoading, run } = useGetTaskRun(runId);

  return <MlTaskRun isLoading={isLoading} run={run} />;
};

export default MlTaskRunContainer;
