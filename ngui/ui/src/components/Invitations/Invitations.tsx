import Grid from "@mui/material/Grid";
import { FormattedMessage } from "react-intl";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Invitation from "components/Invitation";
import TypographyLoader from "components/TypographyLoader";
import InvitationActionsContainer from "containers/InvitationActionsContainer";
import { createGroupsObjectFromArray, isEmpty as isEmptyArray } from "utils/arrays";
import { SPACING_4 } from "utils/layouts";

const Invitations = ({ invitations, onSuccessAccept, onSuccessDecline, isLoading = false, styleProps = {} }) => {
  if (isLoading) {
    return <TypographyLoader linesCount={4} />;
  }

  if (isEmptyArray(invitations)) {
    return <FormattedMessage id="noPendingInvitationsLeft" />;
  }

  return (
    <Grid container direction="column" spacing={SPACING_4}>
      {invitations.map(({ owner_name: name, owner_email: email, id, organization, invite_assignments: assignments }) => {
        const organizationNameInvitedTo = organization;

        const { pool: invitesToPools = [], organization: invitesToOrganization = [] } = createGroupsObjectFromArray(
          assignments,
          "scope_type"
        );

        return (
          <Grid item key={id}>
            <div style={{ marginBottom: "1rem" }}>
              <Invitation
                owner={{ name, email }}
                organizationNameInvitedTo={organizationNameInvitedTo}
                invitesToOrganization={invitesToOrganization}
                invitesToPools={invitesToPools}
              />
            </div>
            <FormButtonsWrapper mt={0} justifyContent={styleProps.buttonsJustifyContent}>
              <InvitationActionsContainer
                invitationId={id}
                onSuccessAccept={onSuccessAccept}
                onSuccessDecline={onSuccessDecline}
              />
            </FormButtonsWrapper>
          </Grid>
        );
      })}
    </Grid>
  );
};

export default Invitations;
