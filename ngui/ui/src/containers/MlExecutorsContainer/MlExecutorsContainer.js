import React from "react";
import MlExecutorsTable from "components/MlExecutorsTable";
import MlExecutorsService from "services/MlExecutorsService";
import { inDateRange, secondsToMilliseconds } from "utils/datetime";

const MlExecutorsContainer = ({ dateRange }) => {
  const getFilteredExecutors = (executors) =>
    executors.filter(({ last_used: lastUsed }) => inDateRange(dateRange, secondsToMilliseconds(lastUsed)));

  const { useGet } = MlExecutorsService();
  const { isLoading, executors } = useGet();

  return <MlExecutorsTable executors={getFilteredExecutors(executors)} isLoading={isLoading} />;
};

export default MlExecutorsContainer;
