import React from "react";
import PropTypes from "prop-types";
import { useNavigate } from "react-router-dom";
import DeleteEntity from "components/DeleteEntity";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlApplicationsService from "services/MlApplicationsService";
import { ML_APPLICATIONS } from "urls";

const MlDeleteApplicationContainer = ({ name, id, onCancel }) => {
  const navigate = useNavigate();
  const { isDemo } = useOrganizationInfo();

  const { useDeleteApplication } = MlApplicationsService();
  const { onDelete, isLoading } = useDeleteApplication();

  const redirectToApplicationsOverview = () => navigate(ML_APPLICATIONS);

  const onApplicationDelete = () => {
    onDelete(id).then(() => {
      redirectToApplicationsOverview();
    });
  };

  return (
    <DeleteEntity
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: onApplicationDelete,
        disabled: isDemo,
        tooltip: { show: isDemo, messageId: "notAvailableInLiveDemo" }
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteMlApplicationQuestion",
        values: {
          application: name,
          strong: (chunks) => <strong>{chunks}</strong>
        }
      }}
    />
  );
};

MlDeleteApplicationContainer.propTypes = {
  name: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default MlDeleteApplicationContainer;
