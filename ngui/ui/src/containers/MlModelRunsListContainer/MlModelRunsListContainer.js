import React from "react";
import { useParams } from "react-router-dom";
import MlModelRunsList from "components/MlModelRunsList";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";
import { getModelRuns } from "utils/mlDemoData/utils";

const DemoContainer = () => {
  const { modelId } = useParams();

  return <MlModelRunsList runs={getModelRuns(modelId)} />;
};

const Container = () => {
  const { modelId } = useParams();

  const { useGetModelRunsList } = MlModelsService();
  const { runs = [], isLoading, isDataReady } = useGetModelRunsList(modelId);

  return <MlModelRunsList runs={runs} isLoading={isLoading || !isDataReady} />;
};

const MlModelRunsListContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlModelRunsListContainer;
