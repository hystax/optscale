import React from "react";
import MlExecutorsTable from "components/MlExecutorsTable";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlExecutorsService from "services/MlExecutorsService";
import { getExecutors } from "utils/mlDemoData/utils";

const DemoContainer = () => <MlExecutorsTable executors={getExecutors()} isLoading={false} />;

const Container = () => {
  const { useGet } = MlExecutorsService();
  const { isLoading, executors } = useGet();

  return <MlExecutorsTable executors={executors} isLoading={isLoading} />;
};

const MlExecutorsContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlExecutorsContainer;
