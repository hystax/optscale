import EditModelVersionPathForm from "components/forms/EditModelVersionPathForm";
import MlModelsService, { ModelVersion } from "services/MlModelsService";

type EditModelVersionAliasFormContainerProps = {
  modelId: string;
  modelVersion: ModelVersion;
  onCancel: () => void;
  onSuccess: () => void;
};

const EditModelVersionPathFormContainer = ({
  modelId,
  modelVersion,
  onCancel,
  onSuccess
}: EditModelVersionAliasFormContainerProps) => {
  const { useUpdateModelVersion } = MlModelsService();
  const { onUpdate, isLoading } = useUpdateModelVersion();

  return (
    <EditModelVersionPathForm
      modelVersion={modelVersion}
      onSubmit={(formData) => onUpdate(modelId, modelVersion.run.id, formData).then(onSuccess)}
      onCancel={onCancel}
      isLoadingProps={{
        isSubmitLoading: isLoading
      }}
    />
  );
};

export default EditModelVersionPathFormContainer;
