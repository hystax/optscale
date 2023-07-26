import React from "react";
import { useParams } from "react-router-dom";
import MlModelDetails from "components/MlModelDetails";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";
import { getModel } from "utils/mlDemoData/utils";

const Container = () => {
  const { modelId } = useParams();

  const { useGetOne } = MlModelsService();

  const { model, isLoading } = useGetOne(modelId);

  return <MlModelDetails isLoading={isLoading} model={model} />;
};

const DemoContainer = () => {
  const { modelId } = useParams();

  return <MlModelDetails model={getModel(modelId)} />;
};

const MlModelDetailsContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlModelDetailsContainer;
