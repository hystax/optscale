import { useNavigate } from "react-router-dom";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import MlRunsetTemplateForm from "components/MlRunsetTemplateForm";
import { FIELD_NAMES } from "components/MlRunsetTemplateForm/FormElements";
import { useApiData } from "hooks/useApiData";
import MlModelsService from "services/MlModelsService";
import MlRunsetTemplatesService from "services/MlRunsetTemplatesService";
import { ML_RUNSET_TEMPLATES } from "urls";

const {
  MODELS_FIELD_NAME,
  DATA_SOURCES_FIELD_NAME,
  REGIONS_FIELD_NAME,
  INSTANCE_TYPES_FIELD_NAME,
  NAME_FIELD_NAME,
  RESOURCE_NAME_PREFIX_NAME,
  MAXIMUM_RUNSET_BUDGET_FIELD_NAME,
  CUSTOM_TAG_KEY_NAME,
  CUSTOM_TAG_VALUE_NAME,
  HYPERPARAMETERS_ARRAY_FIELD_NAME,
  HYPERPARAMETER_NAME_FIELD_NAME,
  HYPERPARAMETER_ENVIRONMENT_VARIABLE_FIELD_NAME
} = FIELD_NAMES;

const defaultValues = {
  [NAME_FIELD_NAME]: "",
  [MAXIMUM_RUNSET_BUDGET_FIELD_NAME]: "",
  [RESOURCE_NAME_PREFIX_NAME]: "",
  [CUSTOM_TAG_KEY_NAME]: "",
  [CUSTOM_TAG_VALUE_NAME]: "",
  [HYPERPARAMETERS_ARRAY_FIELD_NAME]: [
    { [HYPERPARAMETER_NAME_FIELD_NAME]: "", [HYPERPARAMETER_ENVIRONMENT_VARIABLE_FIELD_NAME]: "" }
  ],
  [MODELS_FIELD_NAME]: [],
  [DATA_SOURCES_FIELD_NAME]: [],
  [REGIONS_FIELD_NAME]: [],
  [INSTANCE_TYPES_FIELD_NAME]: []
};

const MlRunsetTemplateCreateFormContainer = () => {
  const navigate = useNavigate();

  const redirect = () => navigate(ML_RUNSET_TEMPLATES);

  const { useGetAll } = MlModelsService();
  const { isLoading: isGetAllModelsLoading, models } = useGetAll();

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
      models={models}
      dataSources={dataSources}
      isLoading={{
        isGetAllModelsLoading,
        isSubmitLoading: isCreateMlRunsetTemplateLoading
      }}
      onSubmit={onSubmit}
      onCancel={onCancel}
      defaultValues={defaultValues}
    />
  );
};

export default MlRunsetTemplateCreateFormContainer;
