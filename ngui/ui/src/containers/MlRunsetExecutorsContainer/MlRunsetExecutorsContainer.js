import React from "react";
import { useParams } from "react-router-dom";
import Executors from "components/MlRunsetOverview/Components/Tabs/Executors";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlRunsetsService from "services/MlRunsetsService";
import { getRunset, getRunsetExecutors } from "utils/mlDemoData/utils";

const DemoContainer = () => {
  const { runsetId } = useParams();

  const runset = getRunset(runsetId);

  const { runs } = runset;

  const data = getRunsetExecutors(runs.map(({ id }) => id));

  return <Executors executors={data} />;
};

const Container = () => {
  const { runsetId } = useParams();

  const { useGetRunners } = MlRunsetsService();

  const { isLoading, executors } = useGetRunners(runsetId);

  return <Executors isLoading={isLoading} executors={executors} />;
};

const MlRunsetExecutorsContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlRunsetExecutorsContainer;
