import React from "react";
import { useParams } from "react-router-dom";
import MlModelRun from "components/MlModelRun";
import MlModelsService from "services/MlModelsService";

const MlModelRunContainer = () => {
  const { runId } = useParams();

  const { useGetModelRun } = MlModelsService();

  const { isLoading, run } = useGetModelRun(runId);

  return <MlModelRun isLoading={isLoading} run={run} />;
};

export default MlModelRunContainer;
