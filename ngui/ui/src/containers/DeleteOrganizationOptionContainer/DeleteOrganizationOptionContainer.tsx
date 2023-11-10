import DeleteEntity from "components/DeleteEntity";
import OrganizationOptionsService from "services/OrganizationOptionsService";

const DeleteOrganizationOptionContainer = ({ name, onCancel }) => {
  const { useDeleteOption } = OrganizationOptionsService();
  const { isDeleteOrganizationOptionLoading, deleteOption } = useDeleteOption();

  return (
    <DeleteEntity
      onCancel={onCancel}
      isLoading={isDeleteOrganizationOptionLoading}
      deleteButtonProps={{
        onDelete: () => deleteOption(name, onCancel)
      }}
      message={{
        messageId: "deleteOrganizationOptionQuestion",
        values: { name: <strong>{name}</strong> }
      }}
    />
  );
};

export default DeleteOrganizationOptionContainer;
