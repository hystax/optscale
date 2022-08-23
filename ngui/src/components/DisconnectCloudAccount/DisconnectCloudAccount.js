import React from "react";
import PropTypes from "prop-types";
import DeleteEntity from "components/DeleteEntity";
import { useDataSources } from "hooks/useDataSources";

const DisconnectCloudAccount = ({ id, type, onCancel, isLoading, onSubmit }) => {
  const { disconnectQuestionId } = useDataSources(type);

  return (
    <DeleteEntity
      message={{
        messageId: disconnectQuestionId
      }}
      dataTestIds={{
        text: "p_disconnect",
        cancelButton: "btn_cancel",
        deleteButton: "btn_disconnect_data_source"
      }}
      isLoading={isLoading}
      deleteButtonProps={{
        messageId: "disconnect",
        onDelete: () => onSubmit(id)
      }}
      onCancel={onCancel}
    />
  );
};

DisconnectCloudAccount.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  onSubmit: PropTypes.func.isRequired,
  id: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired,
  type: PropTypes.string.isRequired
};

export default DisconnectCloudAccount;
