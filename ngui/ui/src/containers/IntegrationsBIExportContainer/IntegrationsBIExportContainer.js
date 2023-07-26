import React from "react";
import BIExport from "components/Integrations/BIExport";
import BIExportService from "services/BIExportService";

const IntegrationsBIExportContainer = () => {
  const { useGetAll } = BIExportService();

  const { isLoading, organizationBIExports = [] } = useGetAll();

  return <BIExport isLoading={isLoading} exportsCount={organizationBIExports.length} />;
};

export default IntegrationsBIExportContainer;
