import React from "react";
import NavigationIcon from "@mui/icons-material/Navigation";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import Button from "components/Button";
import ConditionWrapper from "components/ConditionWrapper";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import GridContainerWithNegativeMarginCompensation from "components/GridContainerWithNegativeMarginCompensation";
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
    <GridContainerWithNegativeMarginCompensation direction="column" alignItems="center" spacing={SPACING_6}>
      <ConditionWrapper
        condition={sendState === ERROR}
        conditionTemplate={
          <Grid item xs={12}>
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
          </Grid>
        }
      >
        <Grid item xs={12}>
          <Logo width={200} />
        </Grid>
        <Grid xs={12} item>
          <div style={{ marginBottom: "1rem" }}>
            <Invitation
              owner={{ name: ownerName, email: ownerEmail }}
              organizationNameInvitedTo={organization}
              invitesToOrganization={invitesToOrganization}
              invitesToPools={invitesToPools}
            />
          </div>
          <FormButtonsWrapper withTopMargin={false} justifyContent="center">
            <InvitationActionsContainer
              invitationId={invitationId}
              onSuccessAccept={onSuccessAccept}
              onSuccessDecline={onSuccessDecline}
            />
          </FormButtonsWrapper>
        </Grid>
      </ConditionWrapper>
    </GridContainerWithNegativeMarginCompensation>
  );
};

AcceptInvitation.propTypes = {
  invitation: PropTypes.object.isRequired,
  sendState: PropTypes.string.isRequired,
  isUpdateLoading: PropTypes.bool.isRequired,
  onSuccessAccept: PropTypes.func,
  onSuccessDecline: PropTypes.func
};

export default AcceptInvitation;
