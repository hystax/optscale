import React from "react";
import ProfilingIntegration from "components/ProfilingIntegration/ProfilingIntegration";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlProfilingService from "services/MlProfilingService";

const DemoContainer = () => <ProfilingIntegration profilingToken="<token>" />;

const Container = () => {
  const { useGetToken } = MlProfilingService();

  const { isLoading, token } = useGetToken();

  return <ProfilingIntegration isLoading={isLoading} profilingToken={token} />;
};

const ProfilingIntegrationContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default ProfilingIntegrationContainer;
