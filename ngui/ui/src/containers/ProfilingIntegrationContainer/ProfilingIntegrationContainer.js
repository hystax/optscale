import React from "react";
import ProfilingIntegration from "components/ProfilingIntegration/ProfilingIntegration";
import MlProfilingService from "services/MlProfilingService";

const ProfilingIntegrationContainer = ({ modelKey }) => {
  const { useGetToken } = MlProfilingService();

  const { isLoading, token } = useGetToken();

  return <ProfilingIntegration isLoading={isLoading} modelKey={modelKey} profilingToken={token} />;
};

export default ProfilingIntegrationContainer;
