import React from "react";
import MlExecutorsTable from "components/MlExecutorsTable";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlExecutorsService from "services/MlExecutorsService";
import { inDateRange, secondsToMilliseconds } from "utils/datetime";
import { getExecutors } from "utils/mlDemoData/utils";

const DemoContainer = ({ getFilteredExecutors }) => (
  <MlExecutorsTable executors={getFilteredExecutors(getExecutors())} isLoading={false} />
);

const Container = ({ getFilteredExecutors }) => {
  const { useGet } = MlExecutorsService();
  const { isLoading, executors } = useGet();

  return <MlExecutorsTable executors={getFilteredExecutors(executors)} isLoading={isLoading} />;
};

const MlExecutorsContainer = ({ dateRange }) => {
  const { isDemo } = useOrganizationInfo();

  const getFilteredExecutors = (executors) =>
    executors.filter(({ last_used: lastUsed }) => inDateRange(dateRange, secondsToMilliseconds(lastUsed)));

  return isDemo ? (
    <DemoContainer getFilteredExecutors={getFilteredExecutors} />
  ) : (
    <Container getFilteredExecutors={getFilteredExecutors} />
  );
};

export default MlExecutorsContainer;
