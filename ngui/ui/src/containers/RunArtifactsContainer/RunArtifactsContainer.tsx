import { useParams } from "react-router-dom";
import RunArtifactsTable from "components/RunArtifactsTable";
import MlArtifactsContainer from "containers/MlArtifactsContainer";

const RunArtifactsContainer = () => {
  const { runId } = useParams() as { runId: string };

  return (
    <MlArtifactsContainer
      runId={runId}
      render={({ artifacts, pagination, search }) => (
        <RunArtifactsTable artifacts={artifacts} pagination={pagination} search={search} />
      )}
    />
  );
};

export default RunArtifactsContainer;
