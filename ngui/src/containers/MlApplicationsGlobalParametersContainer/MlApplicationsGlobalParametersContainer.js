import React from "react";
import MlApplicationsGlobalParameters from "components/MlApplicationsGlobalParameters";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlApplicationsService from "services/MlApplicationsService";
import { parameters as demoParameters } from "utils/mlDemoData/parameters";

const Container = () => {
  const { useGetGlobalParameters } = MlApplicationsService();

  const { isLoading, parameters } = useGetGlobalParameters();

  return <MlApplicationsGlobalParameters parameters={parameters} isLoading={isLoading} />;
};

const DemoContainer = () => <MlApplicationsGlobalParameters parameters={demoParameters} />;

const MlApplicationsGlobalParametersContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlApplicationsGlobalParametersContainer;
