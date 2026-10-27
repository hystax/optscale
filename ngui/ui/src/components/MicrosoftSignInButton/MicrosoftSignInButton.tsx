import { InteractionStatus } from "@azure/msal-browser";
import { useMsal } from "@azure/msal-react";
import ButtonLoader from "components/ButtonLoader";
import MicrosoftIcon from "icons/MicrosoftIcon";
import { AUTH_PROVIDERS } from "utils/constants";
import { microsoftOAuthConfiguration } from "utils/integrations";

const handleClick = async (instance, callback) => {
  try {
    const { tenantId, idToken } = await instance.loginPopup({ prompt: "select_account" });
    callback({ provider: AUTH_PROVIDERS.MICROSOFT, token: idToken, tenantId });
  } catch (error) {
    console.log("Microsoft login failure ", error);
  }
};

const MicrosoftSignInButton = ({ handleSignIn, isLoading, disabled }) => {
  const { instance, inProgress } = useMsal();

  const environmentNotSet = !microsoftOAuthConfiguration.auth.clientId;

  const renderMicrosoftLogin = () => (
    <ButtonLoader
      variant="outlined"
      messageId="microsoft"
      size="medium"
      onClick={() => {
        handleClick(instance, handleSignIn);
      }}
      startIcon={<MicrosoftIcon />}
      disabled={inProgress === InteractionStatus.Startup || environmentNotSet || disabled}
      fullWidth
      isLoading={isLoading}
      tooltip={{
        show: environmentNotSet,
        messageId: "signInWithMicrosoftIsNotConfigured",
      }}
    />
  );

  return renderMicrosoftLogin();
};

export default MicrosoftSignInButton;
