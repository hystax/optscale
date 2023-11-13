import { useParams } from "react-router-dom";
import MlRunsetOverview from "components/MlRunsetOverview";
import MlRunsetsService from "services/MlRunsetsService";

const MlRunsetOverviewContainer = () => {
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

export default MlRunsetOverviewContainer;
