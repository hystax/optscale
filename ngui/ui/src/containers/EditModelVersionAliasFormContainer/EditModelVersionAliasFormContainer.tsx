import EditModelVersionAliasForm from "components/forms/EditModelVersionAliasForm";
import MlModelsService, { ModelVersion } from "services/MlModelsService";

type EditModelVersionAliasFormContainerProps = {
  modelId: string;
  modelVersion: ModelVersion;
  aliasToVersionMap: Record<string, string>;
  onCancel: () => void;
  onSuccess: () => void;
};

const EditModelVersionAliasFormContainer = ({
  modelId,
  aliasToVersionMap,
  modelVersion,
  onCancel,
  onSuccess
}: EditModelVersionAliasFormContainerProps) => {
  const { useUpdateModelVersion } = MlModelsService();
  const { onUpdate, isLoading } = useUpdateModelVersion();

  return (
    <EditModelVersionAliasForm
      modelVersion={modelVersion}
      aliasToVersionMap={aliasToVersionMap}
      onSubmit={(formData) => onUpdate(modelId, modelVersion.run.id, formData).then(onSuccess)}
      onCancel={onCancel}
      isLoadingProps={{
        isSubmitLoading: isLoading
      }}
    />
  );
};

export default EditModelVersionAliasFormContainer;
