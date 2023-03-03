import React from "react";
import { useParams } from "react-router-dom";
import MlEditApplication from "components/MlEditApplication";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlApplicationsService from "services/MlApplicationsService";
import { getApplicationDetails } from "utils/mlDemoData/utils";

const DemoContainer = () => {
  const { modelId } = useParams();

  return <MlEditApplication application={getApplicationDetails(modelId)} />;
};

const Container = () => {
  const { modelId } = useParams();

  const { useGetOne } = MlApplicationsService();
  const { application, isLoading: isGetOneApplicationLoading } = useGetOne(modelId);

  return <MlEditApplication isLoading={isGetOneApplicationLoading} application={application} />;
};

const MlEditApplicationContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlEditApplicationContainer;
