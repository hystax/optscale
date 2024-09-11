import MlMetrics from "components/MlMetrics";
import MlMetricsService from "services/MlMetricsService";

const MlMetricsContainer = () => {
  const { useGetMlMetrics } = MlMetricsService();

  const { isLoading, metrics } = useGetMlMetrics();

  return <MlMetrics metrics={metrics} isLoading={isLoading} />;
};

export default MlMetricsContainer;
