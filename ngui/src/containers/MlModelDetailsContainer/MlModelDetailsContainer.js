import React from "react";
import { useParams } from "react-router-dom";
import MlModelDetails from "components/MlModelDetails";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlApplicationsService from "services/MlApplicationsService";
import { getApplicationDetails } from "utils/mlDemoData/utils";

const Container = () => {
  const { modelId } = useParams();

  const { useGetOne } = MlApplicationsService();

  const { application, isLoading } = useGetOne(modelId);

  return <MlModelDetails isLoading={isLoading} application={application} modelId={modelId} />;
};

const DemoContainer = () => {
  const { modelId } = useParams();

  return <MlModelDetails application={getApplicationDetails(modelId)} modelId={modelId} />;
};

// TODO ML: Change terminology - model -> application
const MlModelDetailsContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlModelDetailsContainer;
