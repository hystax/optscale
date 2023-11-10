import DeleteEntity from "components/DeleteEntity";

const DeleteResourcePerspective = ({ perspectiveName, onDelete, onCancel, isLoading = false }) => (
  <DeleteEntity
    message={{
      messageId: "deletePerspectiveQuestion",
      values: { perspectiveName, strong: (chunks) => <strong>{chunks}</strong> }
    }}
    deleteButtonProps={{
      onDelete
    }}
    onCancel={onCancel}
    isLoading={isLoading}
  />
);

export default DeleteResourcePerspective;
