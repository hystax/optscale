import React from "react";
import PropTypes from "prop-types";
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

DeleteAssignmentRule.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  onSubmit: PropTypes.func.isRequired,
  closeSideModal: PropTypes.func.isRequired
};

export default DeleteAssignmentRule;
