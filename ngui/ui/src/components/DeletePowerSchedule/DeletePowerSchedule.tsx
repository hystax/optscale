import DeleteEntity from "components/DeleteEntity";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";

type DeletePowerScheduleProps = {
  name: string;
  onSubmit: () => void;
  onCancel: () => void;
  isLoading?: boolean;
};

const DeletePowerSchedule = ({ name, onSubmit, onCancel, isLoading = false }: DeletePowerScheduleProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <DeleteEntity
      onDelete={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        color: "error",
        variant: "contained",
        onDelete: onSubmit,
        disabled: isRestricted,
        tooltip: {
          show: isRestricted,
          value: restrictionReasonMessage,
        },
      }}
      dataTestIds={{
        text: "p_delete_power_schedule",
        deleteButton: "btn_delete_power_schedule",
        cancelButton: "btn_cancel_delete_power_schedule",
      }}
      message={{
        messageId: "deletePowerScheduleQuestion",
        values: {
          name,
          strong: (chunks) => <strong>{chunks}</strong>,
        },
      }}
    />
  );
};

export default DeletePowerSchedule;
