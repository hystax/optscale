import React, { useMemo } from "react";
import { useParams } from "react-router-dom";
import MlExecutorsTable from "components/MlExecutorsTable";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlExecutorsService from "services/MlExecutorsService";
import { getRunExecutors } from "utils/mlDemoData/utils";

const DemoContainer = () => {
  const { runId } = useParams();

  return <MlExecutorsTable executors={getRunExecutors(runId)} />;
};

const Container = () => {
  const { runId } = useParams();

  const { useGet } = MlExecutorsService();

  const runIds = useMemo(() => [runId], [runId]);

  const { isLoading, executors } = useGet({ runIds });

  return <MlExecutorsTable executors={executors} isLoading={isLoading} />;
};

const Executors = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default Executors;
