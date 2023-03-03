import React from "react";
import { useParams } from "react-router-dom";
import MlModelRunsList from "components/MlModelRunsList";

import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlApplicationsService from "services/MlApplicationsService";
import { getApplicationRuns } from "utils/mlDemoData/utils";

const DemoContainer = () => {
  const { modelId } = useParams();

  return <MlModelRunsList runs={getApplicationRuns(modelId)} />;
};

const Container = () => {
  const { modelId } = useParams();

  const { useGetModelRunsList } = MlApplicationsService();
  const { runs = [], isLoading } = useGetModelRunsList(modelId);

  return <MlModelRunsList runs={runs} isLoading={isLoading} />;
};

const MlModelRunsListContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlModelRunsListContainer;
