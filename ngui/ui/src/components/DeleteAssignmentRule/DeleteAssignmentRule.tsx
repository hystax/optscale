import DeleteEntity from "components/DeleteEntity";

const DeleteAssignmentRule = ({ isLoading, closeSideModal, onSubmit }) => (
  <DeleteEntity
    message={{
      messageId: "deleteAssignmentRuleQuestion"
    }}
    isLoading={isLoading}
    deleteButtonProps={{
      onDelete: onSubmit
    }}
    onCancel={closeSideModal}
  />
);

export default DeleteAssignmentRule;
