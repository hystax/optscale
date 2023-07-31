import React from "react";
import MlModelGlobalParameters from "components/MlModelGlobalParameters";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";
import { parameters as demoParameters } from "utils/mlDemoData/parameters";

const Container = () => {
  const { useGetGlobalParameters } = MlModelsService();

  const { isLoading, parameters } = useGetGlobalParameters();

  return <MlModelGlobalParameters parameters={parameters} isLoading={isLoading} />;
};

const DemoContainer = () => <MlModelGlobalParameters parameters={demoParameters} />;

const MlModelGlobalParametersContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlModelGlobalParametersContainer;
