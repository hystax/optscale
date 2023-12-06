import DeleteEntity from "components/DeleteEntity";

const DeletePowerSchedule = ({ name, onSubmit, onCancel, isLoading = false }) => (
  <DeleteEntity
    onDelete={onSubmit}
    onCancel={onCancel}
    isLoading={isLoading}
    deleteButtonProps={{
      color: "error",
      variant: "contained",
      onDelete: onSubmit
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

export default DeletePowerSchedule;
