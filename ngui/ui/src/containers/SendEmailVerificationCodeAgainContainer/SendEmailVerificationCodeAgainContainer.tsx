import SendVerificationCodeAgainMessage from "components/SendVerificationCodeAgainCountdownMessage";
import VerifyEmailService from "services/VerifyEmailService";
import { OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME } from "urls";
import { OPTSCALE_CAPABILITY } from "utils/constants";
import { getSearchParams } from "utils/network";

const SendEmailVerificationCodeAgainContainer = () => {
  const { useSendEmailVerificationCode } = VerifyEmailService();

  const { onSend, isLoading } = useSendEmailVerificationCode();

  const { email, [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: capability } = getSearchParams() as {
    email: string;
    [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: string;
  };

  return (
    <SendVerificationCodeAgainMessage
      onSend={() =>
        onSend(email, {
          [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: Object.values(OPTSCALE_CAPABILITY).includes(capability)
            ? capability
            : undefined,
        })
      }
      sendingVerificationCode={isLoading}
    />
  );
};

export default SendEmailVerificationCodeAgainContainer;
