import { useEffect, useState } from "react";
import { Typography } from "@mui/material";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { MILLISECONDS_IN_SECOND, SECONDS_IN_MINUTE } from "utils/datetime";

type CountdownMessageProps = {
  onCountdownEnd: () => void;
};

type SendVerificationCodeAgainMessageProps = {
  onSend: () => Promise<unknown>;
  sendingVerificationCode?: boolean;
};

const CountdownMessage = ({ onCountdownEnd }: CountdownMessageProps) => {
  const [secondsLeft, setSecondsLeft] = useState(SECONDS_IN_MINUTE);

  useEffect(() => {
    const timerId = setInterval(() => {
      setSecondsLeft((prevSeconds) => {
        if (prevSeconds <= 1) {
          clearInterval(timerId);
          onCountdownEnd();
          return 0;
        }
        return prevSeconds - 1;
      });
    }, MILLISECONDS_IN_SECOND);

    return () => clearInterval(timerId);
  }, [onCountdownEnd]);

  return (
    <FormattedMessage
      id="nextVerificationCodeCanBeSentInXSeconds"
      values={{ seconds: secondsLeft, strong: (chunks) => <strong>{chunks}</strong> }}
    />
  );
};

const SendVerificationCodeAgainMessage = ({
  onSend,
  sendingVerificationCode = false,
}: SendVerificationCodeAgainMessageProps) => {
  const [codeCanBeSent, setCodeCanBeSent] = useState(false);

  const renderText = () => {
    if (sendingVerificationCode) {
      return <FormattedMessage id="sendingVerificationCode" />;
    }

    if (codeCanBeSent) {
      return <FormattedMessage id="sendVerificationCodeAgain" />;
    }

    return <CountdownMessage onCountdownEnd={() => setCodeCanBeSent(true)} />;
  };

  return (
    <Typography>
      <Link
        color="primary"
        onClick={sendingVerificationCode || !codeCanBeSent ? undefined : () => onSend().then(() => setCodeCanBeSent(false))}
        component="button"
        type="button"
        sx={
          sendingVerificationCode || !codeCanBeSent
            ? {
                fontWeight: "normal",
                color: (theme) => theme.palette.text.primary,
                "&:hover": {
                  textDecoration: "none",
                },
                cursor: "default",
              }
            : undefined
        }
      >
        {renderText()}
      </Link>
    </Typography>
  );
};

export default SendVerificationCodeAgainMessage;
