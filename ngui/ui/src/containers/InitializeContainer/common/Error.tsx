import { Typography } from "@mui/material";
import { Box } from "@mui/system";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import MailTo from "components/MailTo";
import { useSignOut } from "hooks/useSignOut";
import { EMAIL_SUPPORT } from "urls";
import { Title } from "./Title";

const Error = () => {
  const signOut = useSignOut();

  return (
    <>
      <Box>
        <Title
          dataTestId="p_issue_occurred_during_initialization_process"
          messageId="anIssueOccurredDuringTheInitializationProcess"
          messageValues={{
            email: <MailTo email={EMAIL_SUPPORT} text={EMAIL_SUPPORT} />,
            br: <br />,
          }}
        />
        <Typography align="center" variant="body2" px={2}>
          <FormattedMessage
            id="pleaseSignInAgainAndIfTheProblemPersists"
            values={{ email: <MailTo email={EMAIL_SUPPORT} text={EMAIL_SUPPORT} /> }}
          />
        </Typography>
      </Box>
      <Box height={60} display="flex" alignItems="center" gap={2}>
        <Button size="medium" messageId="signOut" color="primary" onClick={signOut} />
      </Box>
    </>
  );
};

export default Error;
