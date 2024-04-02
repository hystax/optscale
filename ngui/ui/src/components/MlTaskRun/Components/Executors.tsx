import { useMemo } from "react";
import { useParams } from "react-router-dom";
import MlExecutorsTable from "components/MlExecutorsTable";
import MlExecutorsService from "services/MlExecutorsService";

const Executors = () => {
  const { runId } = useParams();

  const { useGet } = MlExecutorsService();

  const runIds = useMemo(() => [runId], [runId]);

  const { isLoading, executors } = useGet({ runIds });

  return <MlExecutorsTable executors={executors} isLoading={isLoading} />;
};

export default Executors;
