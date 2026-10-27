import { useNavigate, useParams } from "react-router-dom";
import MlRunsetTemplateEdit from "components/MlRunsetTemplateEdit";
import { useAllDataSources } from "hooks/coreData/useAllDataSources";
import MlRunsetTemplatesService from "services/MlRunsetTemplatesService";
import MlTasksService from "services/MlTasksService";
import { getMlRunsetTemplateUrl } from "urls";

const MlRunsetTemplateEditContainer = () => {
  const { templateId } = useParams();

  const navigate = useNavigate();

  const redirect = () => navigate(getMlRunsetTemplateUrl(templateId));

  const { useGetAll } = MlTasksService();
  const { isLoading: isGetAllTasksLoading, tasks } = useGetAll();

  const dataSources = useAllDataSources();

  const { useUpdateRunsetTemplate, useGetOne } = MlRunsetTemplatesService();
  const { onUpdate, isLoading: isUpdateMlRunsetTemplateLoading } = useUpdateRunsetTemplate();
  const { runsetTemplate, isLoading: isGetRunsetTemplateLoading } = useGetOne(templateId);

  const onSubmit = (formData) => {
    onUpdate(templateId, formData).then(() => redirect());
  };

  const onCancel = () => redirect();

  return (
    <MlRunsetTemplateEdit
      tasks={tasks}
      dataSources={dataSources}
      onSubmit={onSubmit}
      onCancel={onCancel}
      runsetTemplate={runsetTemplate}
      isLoading={{
        isGetRunsetTemplateLoading,
        isUpdateMlRunsetTemplateLoading,
        isGetAllTasksLoading,
      }}
    />
  );
};

export default MlRunsetTemplateEditContainer;
