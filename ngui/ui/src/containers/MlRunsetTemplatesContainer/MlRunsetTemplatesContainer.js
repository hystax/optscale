import React from "react";
import MlRunsetTemplatesTable from "components/MlRunsetTemplatesTable";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlRunsetTemplatesService from "services/MlRunsetTemplatesService";
import { getRunsetTemplates } from "utils/mlDemoData/utils";

const DemoContainer = () => <MlRunsetTemplatesTable data={getRunsetTemplates()} />;

const Container = () => {
  const { useGetAll } = MlRunsetTemplatesService();

  const { isLoading, runsetTemplates } = useGetAll();

  return <MlRunsetTemplatesTable data={runsetTemplates} isLoading={isLoading} />;
};

const MlRunsetTemplatesContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlRunsetTemplatesContainer;
