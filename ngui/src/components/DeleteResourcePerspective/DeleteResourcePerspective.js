import React from "react";
import PropTypes from "prop-types";
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

DeleteResourcePerspective.propTypes = {
  perspectiveName: PropTypes.string.isRequired,
  onDelete: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default DeleteResourcePerspective;
