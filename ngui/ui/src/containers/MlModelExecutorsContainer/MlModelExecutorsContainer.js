import React, { useMemo } from "react";
import { useParams } from "react-router-dom";
import MlExecutorsTable from "components/MlExecutorsTable";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlExecutorsService from "services/MlExecutorsService";
import { getModelExecutors } from "utils/mlDemoData/utils";

const DemoContainer = () => {
  const { modelId } = useParams();

  const executors = getModelExecutors(modelId);

  return <MlExecutorsTable executors={executors} />;
};

const Container = () => {
  const { modelId } = useParams();

  const { useGet } = MlExecutorsService();

  const modelIds = useMemo(() => [modelId], [modelId]);

  const { isLoading, executors = [] } = useGet({ modelIds });

  return <MlExecutorsTable isLoading={isLoading} executors={executors} />;
};

const MlModelExecutorsContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlModelExecutorsContainer;
