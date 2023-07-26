import React from "react";
import { useParams } from "react-router-dom";
import MlEditModel from "components/MlEditModel";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";
import { getModel } from "utils/mlDemoData/utils";

const DemoContainer = () => {
  const { modelId } = useParams();

  return <MlEditModel model={getModel(modelId)} />;
};

const Container = () => {
  const { modelId } = useParams();

  const { useGetOne } = MlModelsService();
  const { model, isLoading } = useGetOne(modelId);

  return <MlEditModel isLoading={isLoading} model={model} />;
};

const MlEditModelContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlEditModelContainer;
