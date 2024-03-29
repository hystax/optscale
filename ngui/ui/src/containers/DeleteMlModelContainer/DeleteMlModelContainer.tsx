import DeleteEntity from "components/DeleteEntity";
import MlModelsService from "services/MlModelsService";

type DeleteMlModelContainerProps = {
  onCancel: () => void;
  onSuccess: () => void;
  modelId: string;
  modelName: string;
};

const DeleteMlModelContainer = ({ onCancel, onSuccess, modelId, modelName }: DeleteMlModelContainerProps) => {
  const { useDelete } = MlModelsService();
  const { isLoading, onDelete } = useDelete();

  return (
    <DeleteEntity
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: () =>
          onDelete(modelId).then(() => {
            console.log("success");
            onSuccess();
          })
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteModelQuestion",
        values: {
          name: modelName
        }
      }}
    />
  );
};

export default DeleteMlModelContainer;
