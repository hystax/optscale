import { useParams } from "react-router-dom";
import MlTaskModelVersions from "components/MlTaskModelVersions";
import MlTasksService from "services/MlTasksService";

const MlTaskModelVersionsContainer = () => {
  const { taskId } = useParams() as { taskId: string };

  const { useGetTaskModelVersions } = MlTasksService();
  const { modelVersions = [], isLoading } = useGetTaskModelVersions(taskId);

  return <MlTaskModelVersions modelVersions={modelVersions} isLoading={isLoading} />;
};

export default MlTaskModelVersionsContainer;
