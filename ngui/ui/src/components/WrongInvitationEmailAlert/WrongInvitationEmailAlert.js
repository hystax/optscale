import React from "react";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import NavigationIcon from "@mui/icons-material/Navigation";
import { Box, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import useStyles from "components/AcceptInvitations/AcceptInvitations.styles";
import Button from "components/Button";

const WrongInvitationEmailAlert = ({ invitationEmail, currentEmail, onGoToDashboard, onSignOut }) => {
  const { classes } = useStyles();
  return (
    <>
      <Typography align="center">
        <FormattedMessage
          id="wrongInvitationEmailWarning"
          values={{
            invitationEmail,
            currentEmail,
            strong: (chunks) => <strong>{chunks}</strong>
          }}
        />
      </Typography>
      <Typography align="center">
        <FormattedMessage id="wrongInvitationEmailPleaseSignOut" />
      </Typography>
      <Box className={classes.dashboardButton}>
        <Button
          messageId="signOut"
          size="medium"
          color="primary"
          variant="outlined"
          onClick={onSignOut}
          startIcon={<ExitToAppIcon />}
        />
        <Button
          messageId="goToDashboard"
          size="medium"
          color="primary"
          variant="contained"
          onClick={onGoToDashboard}
          startIcon={<NavigationIcon />}
        />
      </Box>
    </>
  );
};

WrongInvitationEmailAlert.propTypes = {
  invitationEmail: PropTypes.string.isRequired,
  currentEmail: PropTypes.string.isRequired,
  onGoToDashboard: PropTypes.func.isRequired,
  onSignOut: PropTypes.func.isRequired
};

export default WrongInvitationEmailAlert;
