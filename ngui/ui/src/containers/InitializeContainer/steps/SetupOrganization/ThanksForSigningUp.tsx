import { useState } from "react";
import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import SnackbarAlert from "components/SnackbarAlert";
import { useSignOut } from "hooks/useSignOut";
import { isEmptyArray } from "utils/arrays";
import { Title } from "../../common";

const ThanksForSigningUp = ({ refetchInvitations, isInvitationsRefetching }) => {
  const signOut = useSignOut();

  const [showSnackbar, setShowSnackbar] = useState(false);

  return (
    <>
      <Box>
        <Title messageId="thanksForSigningUp" />
        <Title messageId="pleaseAskYourAdministratorToInvite" />
      </Box>
      <Box height={60} display="flex" alignItems="center" gap={2}>
        <ButtonLoader
          size="medium"
          messageId="checkForInvitations"
          color="primary"
          onClick={() =>
            refetchInvitations({
              onSuccess: ({ data }) => {
                const { invitations = [] } = data ?? {};
                if (isEmptyArray(invitations)) {
                  setShowSnackbar(true);
                }
              },
            })
          }
          isLoading={isInvitationsRefetching}
        />
        <Button size="medium" messageId="signOut" color="primary" onClick={signOut} />
      </Box>
      <SnackbarAlert
        body={<FormattedMessage id="noActiveInvitationsFound" />}
        openState={showSnackbar}
        handleClose={() => setShowSnackbar(false)}
        severity="info"
      />
    </>
  );
};

export default ThanksForSigningUp;
