import MlTaskGlobalMetrics from "components/MlTaskGlobalMetrics";
import MlTasksService from "services/MlTasksService";

const MlTaskGlobalMetricsContainer = () => {
  const { useGetGlobalMetrics } = MlTasksService();

  const { isLoading, metrics } = useGetGlobalMetrics();

  return <MlTaskGlobalMetrics metrics={metrics} isLoading={isLoading} />;
};

export default MlTaskGlobalMetricsContainer;
