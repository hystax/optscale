import { useState } from "react";
import { Stack } from "@mui/material";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Greeter from "components/Greeter";
import ConfirmVerificationCodeContainer from "containers/ConfirmVerificationCodeContainer/ConfirmVerificationCodeContainer";
import CreateNewPasswordContainer from "containers/CreateNewPasswordContainer";
import SendVerificationCodeContainer from "containers/SendVerificationCodeContainer";
import { HOME } from "urls";
import { SPACING_2 } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";

const SEND_VERIFICATION_CODE = 0;
const CONFIRM_VERIFICATION_CODE = 1;
const CREATE_NEW_PASSWORD = 2;
const PASSWORD_RECOVERY_SUCCESS = 3;

const PasswordRecovery = () => {
  const [step, setStep] = useState(() => {
    const { email } = getQueryParams() as { email: string };

    if (email) {
      return CONFIRM_VERIFICATION_CODE;
    }

    return SEND_VERIFICATION_CODE;
  });

  const stepContent = {
    [SEND_VERIFICATION_CODE]: (
      <SendVerificationCodeContainer
        onSuccess={(email) => {
          updateQueryParams({
            email
          });
          setStep(CONFIRM_VERIFICATION_CODE);
        }}
      />
    ),
    [CONFIRM_VERIFICATION_CODE]: <ConfirmVerificationCodeContainer onSuccess={() => setStep(CREATE_NEW_PASSWORD)} />,
    [CREATE_NEW_PASSWORD]: <CreateNewPasswordContainer onSuccess={() => setStep(PASSWORD_RECOVERY_SUCCESS)} />,
    [PASSWORD_RECOVERY_SUCCESS]: (
      <Stack spacing={SPACING_2}>
        <div>
          <Typography>
            <FormattedMessage id="passwordChangedSuccessfully" />
          </Typography>
        </div>
        <div>
          <Typography>
            <Link color="primary" to={HOME} component={RouterLink}>
              <FormattedMessage id="proceedToOptScale" />
            </Link>
          </Typography>
        </div>
      </Stack>
    )
  }[step];

  return <Greeter content={stepContent} />;
};

export default PasswordRecovery;
