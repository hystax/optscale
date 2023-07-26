import React from "react";
import { useNavigate } from "react-router-dom";
import CreateBIExport from "components/CreateBIExport";
import BIExportService from "services/BIExportService";
import { BI_EXPORTS } from "urls";

const CreateBIExportContainer = () => {
  const navigate = useNavigate();

  const { useCreate } = BIExportService();
  const { onCreate, isLoading } = useCreate();

  const redirect = () => navigate(BI_EXPORTS);

  const onSubmit = (formData) => {
    onCreate(formData).then(() => redirect());
  };

  return (
    <CreateBIExport
      onSubmit={onSubmit}
      onCancel={redirect}
      isLoadingProps={{
        isSubmitLoading: isLoading
      }}
    />
  );
};

export default CreateBIExportContainer;
