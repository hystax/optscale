import NavigationIcon from "@mui/icons-material/Navigation";
import { Box, Stack } from "@mui/system";
import { useDispatch } from "react-redux";
import { getInvitations } from "api";
import { GET_TOKEN } from "api/auth/actionTypes";
import ButtonLoader from "components/ButtonLoader";
import Invitations from "components/Invitations";
import Logo from "components/Logo";
import { getLoginRedirectionPath } from "containers/AuthorizationContainer/AuthorizationContainer";
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
    <Stack alignItems="center" spacing={SPACING_6}>
      <Box>
        <Logo width={200} />
      </Box>
      <Box pl={2} pr={2}>
        <Invitations
          invitations={invitations}
          styleProps={{ buttonsJustifyContent: "center" }}
          onSuccessAccept={onSuccessAccept}
          onSuccessDecline={onSuccessDecline}
          isLoading={isGetInvitationsLoading}
        />
      </Box>
      <Box>
        <ButtonLoader
          messageId="proceedToOptScale"
          size="medium"
          color="primary"
          variant="contained"
          onClick={() =>
            activateScope(userEmail, {
              getOnSuccessRedirectionPath: ({ userEmail: scopeUserEmail }) => getLoginRedirectionPath(scopeUserEmail)
            })
          }
          isLoading={isGetOrganizationsLoading || isCreateOrganizationLoading || isUpdateInvitationLoading}
          startIcon={<NavigationIcon />}
          customWrapperClass={classes.dashboardButton}
        />
      </Box>
    </Stack>
  );
};

export default AcceptInvitations;
