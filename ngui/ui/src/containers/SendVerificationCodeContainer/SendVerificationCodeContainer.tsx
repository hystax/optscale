import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import SendVerificationCodeForm from "components/forms/SendVerificationCodeForm";
import ResetPasswordServices from "services/ResetPasswordServices";

type SendVerificationCodeContainerProps = {
  onSuccess: (email: string) => void;
};

const SendVerificationCodeContainer = ({ onSuccess }: SendVerificationCodeContainerProps) => {
  const { useSendVerificationCode } = ResetPasswordServices();

  const { onSend, isLoading } = useSendVerificationCode();

  return (
    <Box>
      <Typography>
        <FormattedMessage id="resetPasswordInstructions" />
      </Typography>
      <SendVerificationCodeForm onSubmit={({ email }) => onSend(email).then(() => onSuccess(email))} isLoading={isLoading} />
    </Box>
  );
};

export default SendVerificationCodeContainer;
