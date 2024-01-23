import DeleteEntity from "components/DeleteEntity";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

type DeletePowerScheduleProps = {
  name: string;
  onSubmit: () => void;
  onCancel: () => void;
  isLoading?: boolean;
};

const DeletePowerSchedule = ({ name, onSubmit, onCancel, isLoading = false }: DeletePowerScheduleProps) => {
  const { isDemo } = useOrganizationInfo();

  return (
    <DeleteEntity
      onDelete={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        color: "error",
        variant: "contained",
        onDelete: onSubmit,
        disabled: isDemo,
        tooltip: { show: isDemo, messageId: "notAvailableInLiveDemo" }
      }}
      dataTestIds={{
        text: "p_delete_power_schedule",
        deleteButton: "btn_delete_power_schedule",
        cancelButton: "btn_cancel_delete_power_schedule"
      }}
      message={{
        messageId: "deletePowerScheduleQuestion",
        values: {
          name,
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }}
    />
  );
};

export default DeletePowerSchedule;
