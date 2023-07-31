import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import MlRunsetTemplateEdit from "components/MlRunsetTemplateEdit";
import { useApiData } from "hooks/useApiData";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";
import MlRunsetTemplatesService from "services/MlRunsetTemplatesService";
import { getMlRunsetTemplateUrl } from "urls";
import { getModels, getDataSources, getRunsetTemplate } from "utils/mlDemoData/utils";

const DemoContainer = () => {
  const { templateId } = useParams();

  const navigate = useNavigate();
  const redirect = () => navigate(getMlRunsetTemplateUrl(templateId));

  const models = getModels();

  const dataSources = getDataSources();

  return (
    <MlRunsetTemplateEdit
      models={models}
      dataSources={dataSources}
      onSubmit={() => {}}
      onCancel={redirect}
      runsetTemplate={getRunsetTemplate(templateId)}
    />
  );
};

const Container = () => {
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

const MlRunsetTemplateEditContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlRunsetTemplateEditContainer;
