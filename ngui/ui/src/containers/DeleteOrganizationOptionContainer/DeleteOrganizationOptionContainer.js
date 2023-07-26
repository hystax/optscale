import React from "react";
import PropTypes from "prop-types";
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

DeleteOrganizationOptionContainer.propTypes = {
  name: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired
};

export default DeleteOrganizationOptionContainer;
