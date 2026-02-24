import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import SendVerificationCodeForm from "components/forms/SendVerificationCodeForm";
import ResetPasswordServices from "services/ResetPasswordServices";
import { OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME } from "urls";
import { OPTSCALE_CAPABILITY } from "utils/constants";
import { getSearchParams } from "utils/network";

type SendVerificationCodeContainerProps = {
  onSuccess: (email: string) => void;
};

const SendVerificationCodeContainer = ({ onSuccess }: SendVerificationCodeContainerProps) => {
  const { useSendVerificationCode } = ResetPasswordServices();

  const { onSend, isLoading } = useSendVerificationCode();

  const { [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: capability } = getSearchParams() as {
    [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: string;
  };

  return (
    <Box>
      <Typography>
        <FormattedMessage id="resetPasswordInstructions" />
      </Typography>
      <SendVerificationCodeForm
        onSubmit={({ email }) =>
          onSend(email, {
            [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: Object.values(OPTSCALE_CAPABILITY).includes(capability)
              ? capability
              : undefined,
          }).then(() => onSuccess(email))
        }
        isLoading={isLoading}
      />
    </Box>
  );
};

export default SendVerificationCodeContainer;
