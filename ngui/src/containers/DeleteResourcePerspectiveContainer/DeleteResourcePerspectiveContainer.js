import React from "react";
import PropTypes from "prop-types";
import DeleteResourcePerspective from "components/DeleteResourcePerspective";
import { useOrganizationPerspectives } from "hooks/useOrganizationPerspectives";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import { removeKey } from "utils/objects";

const DeleteResourcePerspectiveContainer = ({ perspectiveName, onCancel, onSuccess }) => {
  const { allPerspectives } = useOrganizationPerspectives();

  const { useUpdateOrganizationPerspectives } = OrganizationOptionsService();

  const { update, isLoading } = useUpdateOrganizationPerspectives();

  const onDelete = () => {
    const newPerspectives = removeKey(allPerspectives, perspectiveName);
    update(newPerspectives, onSuccess);
  };

  return (
    <DeleteResourcePerspective
      perspectiveName={perspectiveName}
      onDelete={onDelete}
      onCancel={onCancel}
      isLoading={isLoading}
    />
  );
};

DeleteResourcePerspectiveContainer.propTypes = {
  perspectiveName: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired
};

export default DeleteResourcePerspectiveContainer;
