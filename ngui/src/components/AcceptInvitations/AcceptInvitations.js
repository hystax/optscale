import React from "react";
import NavigationIcon from "@mui/icons-material/Navigation";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { getInvitations } from "api";
import { GET_TOKEN } from "api/auth/actionTypes";
import ButtonLoader from "components/ButtonLoader";
import GridContainerWithNegativeMarginCompensation from "components/GridContainerWithNegativeMarginCompensation";
import Invitations from "components/Invitations";
import Logo from "components/Logo";
import { useApiData } from "hooks/useApiData";
import { SPACING_6 } from "utils/layouts";
import useStyles from "./AcceptInvitations.styles";

const AcceptInvitations = ({ invitations = [], activateScope, isLoadingProps = {} }) => {
  const dispatch = useDispatch();
  const { classes } = useStyles();

  const {
    apiData: { userEmail }
  } = useApiData(GET_TOKEN);

  const onSuccessAccept = () => dispatch(getInvitations());

  const onSuccessDecline = () => dispatch(getInvitations());

  const {
    isGetInvitationsLoading = false,
    isGetOrganizationsLoading = false,
    isCreateOrganizationLoading = false,
    isUpdateInvitationLoading = false
  } = isLoadingProps;

  return (
    <GridContainerWithNegativeMarginCompensation direction="column" alignItems="center" spacing={SPACING_6}>
      <Grid item xs={12}>
        <Logo width={200} />
      </Grid>
      <Grid xs={12} item>
        <Invitations
          invitations={invitations}
          styleProps={{ buttonsJustifyContent: "center" }}
          onSuccessAccept={onSuccessAccept}
          onSuccessDecline={onSuccessDecline}
          isLoading={isGetInvitationsLoading}
        />
      </Grid>
      <Grid xs={12} item>
        <ButtonLoader
          messageId="goToDashboard"
          size="medium"
          color="primary"
          variant="contained"
          onClick={() => activateScope(userEmail)}
          isLoading={isGetOrganizationsLoading || isCreateOrganizationLoading || isUpdateInvitationLoading}
          startIcon={<NavigationIcon />}
          customWrapperClass={classes.dashboardButton}
        />
      </Grid>
    </GridContainerWithNegativeMarginCompensation>
  );
};

AcceptInvitations.propTypes = {
  activateScope: PropTypes.func.isRequired,
  invitations: PropTypes.array,
  isLoadingProps: PropTypes.object
};

export default AcceptInvitations;
