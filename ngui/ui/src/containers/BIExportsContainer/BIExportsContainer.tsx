import BIExports from "components/BIExports";
import BIExportService from "services/BIExportService";

const BIExportsContainer = () => {
  const { useGetAll } = BIExportService();

  const { isLoading, organizationBIExports } = useGetAll();

  return <BIExports isLoading={isLoading} biExports={organizationBIExports} />;
};

export default BIExportsContainer;
