import NavigationIcon from "@mui/icons-material/Navigation";
import { Box, Stack } from "@mui/system";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import IconError from "components/IconError";
import Invitation from "components/Invitation";
import Logo from "components/Logo";
import InvitationActionsContainer from "containers/InvitationActionsContainer";
import { HOME } from "urls";
import { createGroupsObjectFromArray } from "utils/arrays";
import { ERROR } from "utils/constants";
import { SPACING_6 } from "utils/layouts";

const AcceptInvitation = ({ invitation, sendState, onSuccessAccept, onSuccessDecline }) => {
  const {
    id: invitationId,
    owner_name: ownerName,
    owner_email: ownerEmail,
    invite_assignments: assignments = [],
    organization
  } = invitation;

  const { pool: invitesToPools = [], organization: invitesToOrganization = [] } = createGroupsObjectFromArray(
    assignments,
    "scope_type"
  );

  return (
    <Stack direction="column" alignItems="center" spacing={SPACING_6}>
      {sendState === ERROR ? (
        <Box>
          <IconError messageId="invitationNotFound">
            <Button
              color="primary"
              variant="contained"
              messageId="goToDashboard"
              size="medium"
              link={HOME}
              startIcon={<NavigationIcon />}
            />
          </IconError>
        </Box>
      ) : (
        <>
          <Box>
            <Logo width="200" />
          </Box>
          <Box>
            <Box mb="1rem" pl={2} pr={2}>
              <Invitation
                owner={{ name: ownerName, email: ownerEmail }}
                organizationNameInvitedTo={organization}
                invitesToOrganization={invitesToOrganization}
                invitesToPools={invitesToPools}
              />
            </Box>
            <FormButtonsWrapper mt={0} justifyContent="center">
              <InvitationActionsContainer
                invitationId={invitationId}
                onSuccessAccept={onSuccessAccept}
                onSuccessDecline={onSuccessDecline}
              />
            </FormButtonsWrapper>
          </Box>
        </>
      )}
    </Stack>
  );
};

export default AcceptInvitation;
