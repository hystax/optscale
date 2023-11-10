import { useParams } from "react-router-dom";
import Executors from "components/MlRunsetOverview/Components/Tabs/Executors";
import MlRunsetsService from "services/MlRunsetsService";

const MlRunsetExecutorsContainer = () => {
  const { runsetId } = useParams();

  const { useGetRunners } = MlRunsetsService();

  const { isLoading, executors } = useGetRunners(runsetId);

  return <Executors isLoading={isLoading} executors={executors} />;
};

export default MlRunsetExecutorsContainer;
