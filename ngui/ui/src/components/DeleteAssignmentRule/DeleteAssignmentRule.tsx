import DeleteEntity from "components/DeleteEntity";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";

const DeleteAssignmentRule = ({ isLoading, closeSideModal, onSubmit }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <DeleteEntity
      message={{
        messageId: "deleteAssignmentRuleQuestion",
      }}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: onSubmit,
        disabled: isRestricted,
        tooltip: {
          show: isRestricted,
          value: restrictionReasonMessage,
        },
      }}
      onCancel={closeSideModal}
    />
  );
};

export default DeleteAssignmentRule;
