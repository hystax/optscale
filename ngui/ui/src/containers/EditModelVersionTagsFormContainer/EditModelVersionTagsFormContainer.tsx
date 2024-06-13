import EditModelVersionTagsForm from "components/forms/EditModelVersionTagsForm";
import MlModelsService, { ModelVersion } from "services/MlModelsService";

type EditModelVersionAliasFormContainerProps = {
  modelId: string;
  modelVersion: ModelVersion;
  onCancel: () => void;
  onSuccess: () => void;
};

const EditModelVersionTagsFormContainer = ({
  modelId,
  modelVersion,
  onCancel,
  onSuccess
}: EditModelVersionAliasFormContainerProps) => {
  const { useUpdateModelVersion } = MlModelsService();
  const { onUpdate, isLoading } = useUpdateModelVersion();

  const {
    tags,
    run: { id: runId }
  } = modelVersion;

  return (
    <EditModelVersionTagsForm
      tags={tags}
      onSubmit={(formData) => {
        const tagsObject = Object.fromEntries(formData.tags.map(({ key, value }) => [key, value]));

        return onUpdate(modelId, runId, {
          tags: tagsObject
        }).then(onSuccess);
      }}
      onCancel={onCancel}
      isLoadingProps={{
        isSubmitLoading: isLoading
      }}
    />
  );
};

export default EditModelVersionTagsFormContainer;
