import ProfilingIntegration from "components/ProfilingIntegration/ProfilingIntegration";
import MlProfilingService from "services/MlProfilingService";

const ProfilingIntegrationContainer = ({ taskKey }) => {
  const { useGetToken } = MlProfilingService();

  const { isLoading, token } = useGetToken();

  return <ProfilingIntegration isLoading={isLoading} taskKey={taskKey} profilingToken={token} />;
};

export default ProfilingIntegrationContainer;
