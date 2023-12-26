import { useMemo } from "react";
import { useParams } from "react-router-dom";
import MlExecutorsTable from "components/MlExecutorsTable";
import MlExecutorsService from "services/MlExecutorsService";

const MlModelExecutorsContainer = () => {
  const { taskId } = useParams();

  const { useGet } = MlExecutorsService();

  const modelIds = useMemo(() => [taskId], [taskId]);

  const { isLoading, executors = [] } = useGet({ modelIds });

  return <MlExecutorsTable isLoading={isLoading} executors={executors} />;
};
export default MlModelExecutorsContainer;
