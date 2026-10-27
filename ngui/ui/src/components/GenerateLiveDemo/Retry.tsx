import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import Button from "components/Button";
import MailTo from "components/MailTo";
import PageTitle from "components/PageTitle";
import { reset } from "reducers/route";
import { EMAIL_SUPPORT, LOGIN } from "urls";

type RetryProps = {
  retry: () => void;
};

const Retry = ({ retry }: RetryProps) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  return (
    <>
      <Box>
        <PageTitle dataTestId="title_failed-live-demo" align="center" px={2}>
          <FormattedMessage id="failedLiveDemoMessage" />
        </PageTitle>
        <Typography align="center" variant="body2" px={2}>
          <FormattedMessage
            id="failedLiveDemoMessageTryAgain"
            values={{
              email: <MailTo email={EMAIL_SUPPORT} text={EMAIL_SUPPORT} dataTestId="p_failed_live_demo_email" />,
            }}
          />
        </Typography>
      </Box>
      <Box height={60} display="flex" alignItems="center" gap={2}>
        <Button color="primary" size="medium" messageId="retry" variant="contained" onClick={retry} />
        <Button
          size="medium"
          messageId="signOut"
          onClick={() => {
            dispatch(reset());
            navigate(LOGIN);
          }}
        />
      </Box>
    </>
  );
};

export default Retry;
