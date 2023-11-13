import { useNavigate, useParams } from "react-router-dom";
import EditBIExport from "components/EditBIExport";
import BIExportService from "services/BIExportService";
import { BI_EXPORTS, getBIExportUrl } from "urls";

const EditBIExportContainer = () => {
  const { biExportId } = useParams();
  const navigate = useNavigate();

  const { useGet, useUpdate } = BIExportService();
  const { biExport, isLoading: isGetBIExportLoading } = useGet(biExportId);
  const { onUpdate, isLoading: isUpdateLoading } = useUpdate();

  const onSubmit = (formData) => {
    onUpdate(biExportId, formData).then(() => navigate(BI_EXPORTS));
  };

  return (
    <EditBIExport
      onSubmit={onSubmit}
      onCancel={() => navigate(getBIExportUrl(biExportId))}
      biExport={biExport}
      isLoadingProps={{
        isSubmitLoading: isUpdateLoading,
        isGetDataLoading: isGetBIExportLoading
      }}
    />
  );
};

export default EditBIExportContainer;
