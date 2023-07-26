import React from "react";
import { useParams } from "react-router-dom";
import MlRunsetOverview from "components/MlRunsetOverview";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlRunsetsService from "services/MlRunsetsService";
import { getRunset } from "utils/mlDemoData/utils";

const DemoContainer = () => {
  const { runsetId } = useParams();

  const runset = getRunset(runsetId);
  const { runs = [] } = runset;

  return <MlRunsetOverview runset={getRunset(runsetId)} runsetRuns={runs} stopRunset={() => {}} />;
};

const Container = () => {
  const { runsetId } = useParams();

  const { useGetOne, useGetRuns, useStopRunset } = MlRunsetsService();

  const { isLoading: isGetRunsetLoading, runset } = useGetOne(runsetId);

  const { isLoading: isGetRunsetRunsLoading, runs } = useGetRuns(runsetId);

  const { isLoading: isStopMlRunsetLoading, onStop } = useStopRunset(runsetId);

  return (
    <MlRunsetOverview
      runset={runset}
      runsetRuns={runs}
      isGetRunsetLoading={isGetRunsetLoading}
      isGetRunsetRunsLoading={isGetRunsetRunsLoading}
      isStopMlRunsetLoading={isStopMlRunsetLoading}
      stopRunset={onStop}
    />
  );
};

const MlRunsetOverviewContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlRunsetOverviewContainer;
