import React from "react";
import ProfilingIntegration from "components/ProfilingIntegration/ProfilingIntegration";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlProfilingService from "services/MlProfilingService";

const DemoContainer = ({ modelKey }) => <ProfilingIntegration modelKey={modelKey} profilingToken="<token>" />;

const Container = ({ modelKey }) => {
  const { useGetToken } = MlProfilingService();

  const { isLoading, token } = useGetToken();

  return <ProfilingIntegration isLoading={isLoading} modelKey={modelKey} profilingToken={token} />;
};

const ProfilingIntegrationContainer = ({ modelKey }) => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer modelKey={modelKey} /> : <Container modelKey={modelKey} />;
};

export default ProfilingIntegrationContainer;
