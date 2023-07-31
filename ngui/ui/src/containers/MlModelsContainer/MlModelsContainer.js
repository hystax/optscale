import React from "react";
import MlModels from "components/MlModels";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";
import { getModels } from "utils/mlDemoData/utils";

const DemoContainer = () => <MlModels models={getModels()} />;

const Container = () => {
  const { useGetAll } = MlModelsService();

  const { isLoading, models } = useGetAll();

  return <MlModels models={models} isLoading={isLoading} />;
};

const MlModelsContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlModelsContainer;
