import { useNavigate } from "react-router-dom";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import MlRunsetTemplateForm from "components/forms/MlRunsetTemplateForm";
import { FIELD_NAMES } from "components/forms/MlRunsetTemplateForm/constants";
import { useApiData } from "hooks/useApiData";
import MlRunsetTemplatesService from "services/MlRunsetTemplatesService";
import MlTasksService from "services/MlTasksService";
import { ML_RUNSET_TEMPLATES } from "urls";

const defaultValues = {
  [FIELD_NAMES.NAME]: "",
  [FIELD_NAMES.BUDGET]: "",
  [FIELD_NAMES.RESOURCE_NAME_PREFIX]: "",
  [FIELD_NAMES.TAG_KEY]: "",
  [FIELD_NAMES.TAG_VALUE]: "",
  [FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.FIELD_NAME]: [
    {
      [FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.HYPERPARAMETER_NAME]: "",
      [FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.ENVIRONMENT_VARIABLE]: ""
    }
  ],
  [FIELD_NAMES.TASKS]: [],
  [FIELD_NAMES.DATA_SOURCES]: [],
  [FIELD_NAMES.REGIONS]: [],
  [FIELD_NAMES.INSTANCE_TYPES]: []
};

const MlRunsetTemplateCreateFormContainer = () => {
  const navigate = useNavigate();

  const redirect = () => navigate(ML_RUNSET_TEMPLATES);

  const { useGetAll } = MlTasksService();
  const { isLoading: isGetAllTasksLoading, tasks } = useGetAll();

  const {
    apiData: { cloudAccounts: dataSources = [] }
  } = useApiData(GET_DATA_SOURCES);

  const { useCreateMlRunsetTemplate } = MlRunsetTemplatesService();
  const { onCreate, isLoading: isCreateMlRunsetTemplateLoading } = useCreateMlRunsetTemplate();

  const onSubmit = (formData) => {
    onCreate(formData).then(() => redirect());
  };

  const onCancel = () => redirect();

  return (
    <MlRunsetTemplateForm
      tasks={tasks}
      dataSources={dataSources}
      isLoading={{
        isGetAllTasksLoading,
        isSubmitLoading: isCreateMlRunsetTemplateLoading
      }}
      onSubmit={onSubmit}
      onCancel={onCancel}
      defaultValues={defaultValues}
    />
  );
};

export default MlRunsetTemplateCreateFormContainer;
