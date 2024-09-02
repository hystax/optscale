import { useEffect, useRef, useState } from "react";
import { Typography } from "@mui/material";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import ResetPasswordServices from "services/ResetPasswordServices";
import { SECONDS_IN_MINUTE } from "utils/datetime";
import { getQueryParams } from "utils/network";

type CountdownMessageProps = {
  onCountdownEnd: () => void;
};

const CountdownMessage = ({ onCountdownEnd }: CountdownMessageProps) => {
  const [secondsLeft, setSecondsLeft] = useState(SECONDS_IN_MINUTE);

  const timerRef = useRef(null);

  useEffect(() => {
    timerRef.current = setInterval(() => {
      setSecondsLeft((prev) => prev - 1);
    }, 1000);

    return () => {
      if (timerRef.current !== null) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (secondsLeft <= 0) {
      if (timerRef.current !== null) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }

      onCountdownEnd();
    }
  }, [onCountdownEnd, secondsLeft]);

  return (
    <FormattedMessage
      id="nextVerificationCodeCanBeSentInXSeconds"
      values={{ seconds: secondsLeft, strong: (chunks) => <strong>{chunks}</strong> }}
    />
  );
};

const SendVerificationCodeAgainContainer = () => {
  const { email } = getQueryParams() as { email: string };

  const { useSendVerificationCode } = ResetPasswordServices();

  const { onSend, isLoading } = useSendVerificationCode();

  const [codeCanBeSent, setCodeCanBeSent] = useState(false);

  const renderText = () => {
    if (isLoading) {
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
        onClick={isLoading || !codeCanBeSent ? undefined : () => onSend(email).then(() => setCodeCanBeSent(false))}
        component="button"
        type="button"
        sx={
          isLoading || !codeCanBeSent
            ? {
                fontWeight: "normal",
                color: (theme) => theme.palette.text.primary,
                "&:hover": {
                  textDecoration: "none"
                },
                cursor: "default"
              }
            : undefined
        }
      >
        {renderText()}
      </Link>
    </Typography>
  );
};

export default SendVerificationCodeAgainContainer;
