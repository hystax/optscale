import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import ConfirmVerificationCodeForm from "components/forms/ConfirmVerificationCodeForm/ConfirmVerificationCodeForm";
import ResetPasswordServices from "services/ResetPasswordServices";
import { getQueryParams } from "utils/network";

type ConfirmVerificationCodeContainerProps = {
  onSuccess: () => void;
};

const ConfirmVerificationCodeContainer = ({ onSuccess }: ConfirmVerificationCodeContainerProps) => {
  const { email } = getQueryParams() as { email: string };

  const { useGetVerificationCodeToken } = ResetPasswordServices();

  const { onGet, isLoading } = useGetVerificationCodeToken();

  return (
    <Box>
      <Typography>
        <FormattedMessage id="pleaseEnterVerificationCodeSentTo" />
      </Typography>
      <Typography fontWeight="bold" gutterBottom>
        {email}
      </Typography>
      <ConfirmVerificationCodeForm onSubmit={({ code }) => onGet(email, code).then(onSuccess)} isLoading={isLoading} />
    </Box>
  );
};

export default ConfirmVerificationCodeContainer;
