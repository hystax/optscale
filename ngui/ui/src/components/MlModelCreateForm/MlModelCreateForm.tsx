import { FormProvider, useForm } from "react-hook-form";
import {
  MlModelCreateFormButtons,
  MlModelCreateFormKeyField,
  MlModelCreateFormNameField,
  MlModelCreateFormDescriptionField,
  MlModelCreateFormOwnerField,
  MlModelCreateFormParametersField
} from "./FormElements";

const NAME_FIELD_NAME = "name";
const DESCRIPTION_FIELD_NAME = "description";
const KEY_FIELD_NAME = "key";
const OWNER_FIELD_NAME = "owner_id";
const GOALS_FIELD_NAME = "goals";

const MlModelCreateForm = ({ onSubmit, onCancel, employees = [], parameters, isLoading = {} }) => {
  const { isGetEmployeesLoading = false, isCreateModelLoading = false, isGetGlobalParametersLoading = false } = isLoading;

  const methods = useForm({
    defaultValues: {
      [NAME_FIELD_NAME]: "",
      [DESCRIPTION_FIELD_NAME]: "",
      [KEY_FIELD_NAME]: "",
      [OWNER_FIELD_NAME]: "",
      [GOALS_FIELD_NAME]: []
    }
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form data-test-id="create_model_form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <MlModelCreateFormNameField name={NAME_FIELD_NAME} />
        <MlModelCreateFormDescriptionField name={DESCRIPTION_FIELD_NAME} />
        <MlModelCreateFormKeyField name={KEY_FIELD_NAME} />
        <MlModelCreateFormOwnerField name={OWNER_FIELD_NAME} employees={employees} isLoading={isGetEmployeesLoading} />
        <MlModelCreateFormParametersField
          name={GOALS_FIELD_NAME}
          parameters={parameters}
          isLoading={isGetGlobalParametersLoading}
        />
        <MlModelCreateFormButtons
          onCancel={onCancel}
          isLoading={isGetEmployeesLoading || isCreateModelLoading || isGetGlobalParametersLoading}
        />
      </form>
    </FormProvider>
  );
};

export default MlModelCreateForm;
