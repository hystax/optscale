import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import MlRunsetTemplateEdit from "components/MlRunsetTemplateEdit";
import { useApiData } from "hooks/useApiData";
import MlModelsService from "services/MlModelsService";
import MlRunsetTemplatesService from "services/MlRunsetTemplatesService";
import { getMlRunsetTemplateUrl } from "urls";

const MlRunsetTemplateEditContainer = () => {
  const { templateId } = useParams();

  const navigate = useNavigate();

  const redirect = () => navigate(getMlRunsetTemplateUrl(templateId));

  const { useGetAll } = MlModelsService();
  const { isLoading: isGetAllModelsLoading, models } = useGetAll();

  const {
    apiData: { cloudAccounts: dataSources = [] }
  } = useApiData(GET_DATA_SOURCES);

  const { useUpdateRunsetTemplate, useGetOne } = MlRunsetTemplatesService();
  const { onUpdate, isLoading: isUpdateMlRunsetTemplateLoading } = useUpdateRunsetTemplate();
  const { runsetTemplate, isLoading: isGetRunsetTemplateLoading } = useGetOne(templateId);

  const onSubmit = (formData) => {
    onUpdate(templateId, formData).then(() => redirect());
  };

  const onCancel = () => redirect();

  return (
    <MlRunsetTemplateEdit
      models={models}
      dataSources={dataSources}
      onSubmit={onSubmit}
      onCancel={onCancel}
      runsetTemplate={runsetTemplate}
      isLoading={{
        isGetRunsetTemplateLoading,
        isUpdateMlRunsetTemplateLoading,
        isGetAllModelsLoading
      }}
    />
  );
};

export default MlRunsetTemplateEditContainer;
