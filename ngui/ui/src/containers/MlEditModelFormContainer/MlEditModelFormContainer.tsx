import { useNavigate, useParams } from "react-router-dom";
import { MlEditModelForm } from "components/MlModelForm";
import MlModelsService, { EditModelApiParams, ModelDetails } from "services/MlModelsService";
import { getMlModelUrl } from "urls";

type MlUpdateModelFormContainerProps = {
  model: ModelDetails;
  isModelLoading: boolean;
};

const MlEditModelFormContainer = ({ model, isModelLoading }: MlUpdateModelFormContainerProps) => {
  const { modelId } = useParams() as { modelId: string };
  const navigate = useNavigate();

  const { useUpdate } = MlModelsService();
  const { isLoading: isUpdateLoading, onUpdate } = useUpdate();

  const redirect = () => navigate(getMlModelUrl(modelId));

  const onCancel = () => redirect();

  return (
    <MlEditModelForm
      onSubmit={(formData) => {
        const params: EditModelApiParams = {
          name: formData.name,
          description: formData.description,
          tags: Object.fromEntries(formData.tags.map(({ key, value }) => [key, value]))
        };

        return onUpdate(modelId, params).then(() => redirect());
      }}
      onCancel={onCancel}
      model={model}
      isLoadingProps={{
        isGetDataLoading: isModelLoading,
        isSubmitLoading: isUpdateLoading
      }}
    />
  );
};

export default MlEditModelFormContainer;
