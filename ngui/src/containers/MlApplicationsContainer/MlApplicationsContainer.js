import React from "react";
import MlApplications from "components/MlApplications";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlApplicationsService from "services/MlApplicationsService";
import { getApplicationsDetails } from "utils/mlDemoData/utils";

const DemoContainer = () => <MlApplications applications={getApplicationsDetails()} />;

const Container = () => {
  const { useGetAll } = MlApplicationsService();

  const { isLoading, applications } = useGetAll();

  return <MlApplications applications={applications} isLoading={isLoading} />;
};

const MlApplicationsContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlApplicationsContainer;
