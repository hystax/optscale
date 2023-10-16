import React from "react";
import MlRunsetTemplatesTable from "components/MlRunsetTemplatesTable";
import MlRunsetTemplatesService from "services/MlRunsetTemplatesService";

const MlRunsetTemplatesContainer = () => {
  const { useGetAll } = MlRunsetTemplatesService();

  const { isLoading, runsetTemplates } = useGetAll();

  return <MlRunsetTemplatesTable data={runsetTemplates} isLoading={isLoading} />;
};

export default MlRunsetTemplatesContainer;
