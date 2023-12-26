import React from "react";
import { useNavigate } from "react-router-dom";
import { MlDatasetCreateForm } from "components/MlDatasetForm";
import MlDatasetsService from "services/MlDatasetsService";
import { ML_DATASETS } from "urls";

const MlDatasetCreateFormContainer = () => {
  const navigate = useNavigate();

  const { useCreate } = MlDatasetsService();

  const { isLoading: isCreateDatasetLoading, onCreate } = useCreate();

  const redirect = () => navigate(ML_DATASETS);

  const onSubmit = (formData) => {
    onCreate(formData).then(() => redirect());
  };

  const onCancel = () => redirect();

  return <MlDatasetCreateForm onSubmit={onSubmit} onCancel={onCancel} isLoading={{ isCreateDatasetLoading }} />;
};

export default MlDatasetCreateFormContainer;
