import { useNavigate } from "react-router-dom";
import { MlCreateModelForm } from "components/forms/MlModelForm";
import MlModelsService, { CreateModelApiParams } from "services/MlModelsService";
import { ML_MODELS } from "urls";

const MlCreateModelFormContainer = () => {
  const navigate = useNavigate();

  const { useCreate } = MlModelsService();
  const { isLoading, onCreate } = useCreate();

  const redirect = () => navigate(ML_MODELS);

  const onCancel = () => redirect();

  return (
    <MlCreateModelForm
      onSubmit={(formData) => {
        const params: CreateModelApiParams = {
          name: formData.name,
          key: formData.key,
          description: formData.description,
          tags: Object.fromEntries(formData.tags.map(({ key, value }) => [key, value]))
        };

        return onCreate(params).then(() => redirect());
      }}
      onCancel={onCancel}
      isLoadingProps={{
        isSubmitLoading: isLoading
      }}
    />
  );
};

export default MlCreateModelFormContainer;
