import React, { useEffect, useState } from "react";
import Link from "@mui/material/Link";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useLocation } from "react-router-dom";
import SnackbarAlert from "components/SnackbarAlert";
import { SETTINGS_TABS } from "pages/Settings/Settings";
import InvitationsService from "services/InvitationsService";
import { getSettingsUrl, ACCEPT_INVITATIONS } from "urls";
import { isEmpty } from "utils/arrays";

const AlertContainer = () => {
  const { useGet } = InvitationsService();

  const { invitations } = useGet();

  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(!isEmpty(invitations));
  }, [invitations]);

  const handleClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpen(false);
  };

  const alertSeverity = "info";
  const theme = useTheme();

  return (
    <SnackbarAlert
      body={
        <FormattedMessage
          id="pendingInvitations"
          values={{
            invitations: invitations.length,
            invitationsTab: (chunks) => (
              <Link
                style={{ color: theme.palette[alertSeverity].contrastText }}
                onClick={handleClose}
                to={getSettingsUrl(SETTINGS_TABS.INVITATIONS)}
                component={RouterLink}
              >
                {chunks}
              </Link>
            )
          }}
        />
      }
      openState={open}
      severity={alertSeverity}
      handleClose={handleClose}
      autoHideDuration={undefined}
    />
  );
};

const PendingInvitationsAlertContainer = () => {
  const { pathname } = useLocation();
  const blacklist = [ACCEPT_INVITATIONS];

  return blacklist.includes(pathname) ? null : <AlertContainer />;
};

export default PendingInvitationsAlertContainer;
