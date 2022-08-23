import React from "react";
import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseOutlinedIcon from "@mui/icons-material/CloseOutlined";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { updateInvitation } from "api";
import { UPDATE_INVITATION } from "api/restapi/actionTypes";
import ButtonLoader from "components/ButtonLoader";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const InvitationActionsContainer = ({ invitationId, onSuccessAccept, onSuccessDecline, buttonSize = "small" }) => {
  const dispatch = useDispatch();

  const { isLoading, entityId } = useApiState(UPDATE_INVITATION);

  const onAccept = () => {
    dispatch((_, getState) => {
      dispatch(updateInvitation(invitationId, "accept")).then(() => {
        if (typeof onSuccessAccept === "function" && !isError(UPDATE_INVITATION, getState())) {
          onSuccessAccept();
        }
        return undefined;
      });
    });
  };

  const onDecline = () => {
    dispatch((_, getState) => {
      dispatch(updateInvitation(invitationId, "decline")).then(() => {
        if (typeof onSuccessDecline === "function" && !isError(UPDATE_INVITATION, getState())) {
          onSuccessDecline();
        }
        return undefined;
      });
    });
  };

  const isButtonLoading = entityId === invitationId && isLoading;

  return (
    <>
      <ButtonLoader
        size={buttonSize}
        messageId="accept"
        color="success"
        variant="contained"
        onClick={onAccept}
        isLoading={isButtonLoading}
        startIcon={<CheckOutlinedIcon />}
      />
      <ButtonLoader
        size={buttonSize}
        messageId="decline"
        color="error"
        onClick={onDecline}
        isLoading={isButtonLoading}
        startIcon={<CloseOutlinedIcon />}
      />
    </>
  );
};

InvitationActionsContainer.propTypes = {
  invitationId: PropTypes.string.isRequired,
  onSuccessAccept: PropTypes.func,
  onSuccessDecline: PropTypes.func,
  buttonSize: PropTypes.string
};

export default InvitationActionsContainer;
