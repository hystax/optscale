import NavigationIcon from "@mui/icons-material/Navigation";
import { Box } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import ButtonLoader from "components/ButtonLoader";
import Invitations from "components/Invitations";
import { SPACING_1, SPACING_2 } from "utils/layouts";

const useStyles = makeStyles()((theme) => ({
  dashboardButton: {
    [theme.breakpoints.up("md")]: {
      position: "absolute",
      right: 40,
      bottom: 40,
    },
    padding: theme.spacing(SPACING_2),
    "& > *:not(:last-child)": {
      marginRight: theme.spacing(SPACING_1),
    },
  },
}));

const AcceptInvitations = ({ invitations, refetchInvitations, onProceed }) => {
  const { classes } = useStyles();

  return (
    <>
      <Box pl={2} pr={2}>
        <Invitations
          invitations={invitations}
          styleProps={{ buttonsJustifyContent: "center" }}
          onSuccessAccept={() => {
            refetchInvitations();
          }}
          onSuccessDecline={() => {
            refetchInvitations();
          }}
          isLoading={false}
        />
      </Box>
      <Box>
        <ButtonLoader
          dataTestId="btn_proceed_to_optscale"
          messageId="proceedToOptScale"
          size="medium"
          color="primary"
          variant="contained"
          onClick={onProceed}
          startIcon={<NavigationIcon />}
          customWrapperClass={classes.dashboardButton}
        />
      </Box>
    </>
  );
};

export default AcceptInvitations;
