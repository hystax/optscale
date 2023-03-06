import React from "react";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { MlDeleteApplicationModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const DeleteApplicationButton = ({ id, name }) => {
  const openSideModal = useOpenSideModal();

  return (
    <Button
      dataTestId="btn_delete"
      variant="contained"
      color="error"
      messageId="delete"
      onClick={() =>
        openSideModal(MlDeleteApplicationModal, {
          name,
          id
        })
      }
    />
  );
};

const MlEditApplicationFormButtons = ({ applicationId, applicationName, onCancel, isLoading = false }) => {
  const { isDemo } = useOrganizationInfo();

  return (
    <FormButtonsWrapper justifyContent="space-between">
      <Box display="flex">
        <ButtonLoader
          messageId="save"
          dataTestId="btn_save"
          color="primary"
          variant="contained"
          type="submit"
          disabled={isDemo}
          isLoading={isLoading}
          tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
        />
        <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
      </Box>
      <DeleteApplicationButton id={applicationId} name={applicationName} />
    </FormButtonsWrapper>
  );
};

MlEditApplicationFormButtons.propTypes = {
  applicationId: PropTypes.string,
  applicationName: PropTypes.string,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default MlEditApplicationFormButtons;
