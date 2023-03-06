import React, { useMemo } from "react";
import { useParams } from "react-router-dom";
import MlExecutorsTable from "components/MlExecutorsTable";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlExecutorsService from "services/MlExecutorsService";
import { getApplicationExecutors } from "utils/mlDemoData/utils";

const DemoContainer = () => {
  const { modelId: applicationId } = useParams();

  const executors = getApplicationExecutors(applicationId);

  return <MlExecutorsTable executors={executors} />;
};

const Container = () => {
  const { modelId: applicationId } = useParams();

  const { useGet } = MlExecutorsService();

  const applicationIds = useMemo(() => [applicationId], [applicationId]);

  const { isLoading, executors = [] } = useGet({ applicationIds });

  return <MlExecutorsTable isLoading={isLoading} executors={executors} />;
};

const MlModelExecutorsContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlModelExecutorsContainer;
