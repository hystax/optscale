import React from "react";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { deleteCalendarSynchronization } from "api";
import { DELETE_CALENDAR_SYNCHRONIZATION } from "api/restapi/actionTypes";
import DeleteEntity from "components/DeleteEntity";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const DisconnectGoogleCalendarContainer = ({ id, onCancel, shareableLink }) => {
  const { isLoading } = useApiState(DELETE_CALENDAR_SYNCHRONIZATION);
  const dispatch = useDispatch();

  const onSubmit = () =>
    dispatch((_, getState) => {
      dispatch(deleteCalendarSynchronization(id)).then(() => {
        if (!isError(DELETE_CALENDAR_SYNCHRONIZATION, getState())) {
          onCancel();
        }
      });
    });

  return (
    <DeleteEntity
      onDelete={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        color: "error",
        variant: "contained",
        messageId: "disconnect",
        onDelete: onSubmit
      }}
    >
      <Box mb={2}>
        <Typography>
          <FormattedMessage
            id="disconnectGoogleCalendarMessage"
            values={{
              link: (
                <Link href={shareableLink} target="_blank" rel="noopener">
                  {shareableLink}
                </Link>
              )
            }}
          />
        </Typography>
      </Box>
      <Typography>
        <FormattedMessage id="youWillBeAbleToConnectAgain" />
      </Typography>
    </DeleteEntity>
  );
};

DisconnectGoogleCalendarContainer.propTypes = {
  id: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired,
  shareableLink: PropTypes.string.isRequired
};

export default DisconnectGoogleCalendarContainer;
