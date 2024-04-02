import { useMemo } from "react";
import { useParams } from "react-router-dom";
import MlExecutorsTable from "components/MlExecutorsTable";
import MlExecutorsService from "services/MlExecutorsService";

const MlTaskExecutorsContainer = () => {
  const { taskId } = useParams();

  const { useGet } = MlExecutorsService();

  const taskIds = useMemo(() => [taskId], [taskId]);

  const { isLoading, executors = [] } = useGet({ taskIds });

  return <MlExecutorsTable isLoading={isLoading} executors={executors} />;
};
export default MlTaskExecutorsContainer;
