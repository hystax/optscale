import { useState } from "react";
import { Stack } from "@mui/material";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import Greeter from "components/Greeter";
import ConfirmVerificationCodeContainer from "containers/ConfirmVerificationCodeContainer/ConfirmVerificationCodeContainer";
import CreateNewPasswordContainer from "containers/CreateNewPasswordContainer";
import { initialize } from "containers/InitializeContainer/redux";
import SendVerificationCodeContainer from "containers/SendVerificationCodeContainer";
import { INITIALIZE, OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME } from "urls";
import { SPACING_2 } from "utils/layouts";
import macaroon from "utils/macaroons";
import { stringifySearchParams, getSearchParams, updateSearchParams } from "utils/network";

const SEND_VERIFICATION_CODE = 0;
const CONFIRM_VERIFICATION_CODE = 1;
const CREATE_NEW_PASSWORD = 2;
const PASSWORD_RECOVERY_SUCCESS = 3;

const PasswordRecovery = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const [step, setStep] = useState(() => {
    const { email } = getSearchParams() as { email: string };

    if (email) {
      return CONFIRM_VERIFICATION_CODE;
    }

    return SEND_VERIFICATION_CODE;
  });

  const [temporaryVerificationCodeToken, setTemporaryVerificationCodeToken] = useState<{
    user_id: string;
    user_email: string;
    token: string;
  }>();

  const [verificationCodeToken, setVerificationCodeToken] = useState<{
    user_id: string;
    user_email: string;
    token: string;
  }>();

  const stepContent = {
    [SEND_VERIFICATION_CODE]: (
      <SendVerificationCodeContainer
        onSuccess={(email) => {
          updateSearchParams({
            email,
          });
          setStep(CONFIRM_VERIFICATION_CODE);
        }}
      />
    ),
    [CONFIRM_VERIFICATION_CODE]: (
      <ConfirmVerificationCodeContainer
        onSuccess={(token) => {
          setStep(CREATE_NEW_PASSWORD);
          setTemporaryVerificationCodeToken(token);
        }}
      />
    ),
    [CREATE_NEW_PASSWORD]: (
      <CreateNewPasswordContainer
        verificationCodeToken={temporaryVerificationCodeToken}
        onSuccess={(token) => {
          setVerificationCodeToken(token);
          setStep(PASSWORD_RECOVERY_SUCCESS);
        }}
      />
    ),
    [PASSWORD_RECOVERY_SUCCESS]: (
      <Stack spacing={SPACING_2}>
        <div>
          <Typography>
            <FormattedMessage id="passwordChangedSuccessfully" />
          </Typography>
        </div>
        <div>
          <Typography>
            <Link
              color="primary"
              component="button"
              onClick={() => {
                const caveats = macaroon.processCaveats(macaroon.deserialize(verificationCodeToken.token).getCaveats());
                dispatch(initialize({ ...verificationCodeToken, caveats }));

                const { [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: capability } = getSearchParams() as {
                  [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: string;
                };

                navigate(
                  `${INITIALIZE}?${stringifySearchParams({
                    [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: capability,
                  })}`
                );
              }}
            >
              <FormattedMessage id="proceedToOptScale" />
            </Link>
          </Typography>
        </div>
      </Stack>
    ),
  }[step];

  return <Greeter content={stepContent} />;
};

export default PasswordRecovery;
