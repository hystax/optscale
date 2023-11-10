import { useParams } from "react-router-dom";
import BIExport from "components/BIExport";
import BIExportService from "services/BIExportService";

const BIExportContainer = () => {
  const { biExportId } = useParams();

  const { useGet } = BIExportService();

  const { isLoading, biExport } = useGet(biExportId);

  return <BIExport isLoading={isLoading} biExport={biExport} />;
};

export default BIExportContainer;
