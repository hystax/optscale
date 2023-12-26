import React from "react";
import DeleteEntity from "components/DeleteEntity";
import LayoutsService from "services/LayoutsService";

const DeleteMlChartsDashboardContainer = ({ dashboard, removeDashboard, onCancel }) => {
  const onDelete = () => removeDashboard(dashboard.id).then(onCancel);

  const { useDelete } = LayoutsService();
  const { isLoading: isDeleteLoading } = useDelete();

  return (
    <DeleteEntity
      onDelete={onDelete}
      onCancel={onCancel}
      isLoading={isDeleteLoading}
      deleteButtonProps={{
        color: "error",
        variant: "contained",
        onDelete
      }}
      dataTestIds={{
        text: "p_delete_dashboard",
        deleteButton: "btn_delete_dashboard_delete",
        cancelButton: "btn_delete_dashboard_cancel"
      }}
      message={{
        messageId: "deleteDashboardQuestion",
        values: { name: dashboard.name, strong: (chunks) => <strong>{chunks}</strong> }
      }}
    />
  );
};

export default DeleteMlChartsDashboardContainer;
