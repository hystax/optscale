import { InteractionStatus } from "@azure/msal-browser";
import { useMsal } from "@azure/msal-react";
import ButtonLoader from "components/ButtonLoader";
import { PROVIDERS } from "hooks/useNewAuthorization";
import MicrosoftIcon from "icons/MicrosoftIcon";
import { microsoftOAuthConfiguration } from "utils/integrations";

const handleClick = async (instance, callback, setIsAuthInProgress) => {
  try {
    const { tenantId, idToken } = await instance.loginPopup({ prompt: "select_account" });
    callback(PROVIDERS.MICROSOFT, { token: idToken, tenant_id: tenantId });
  } catch (error) {
    console.log("Microsoft login failure ", error);
    setIsAuthInProgress(false);
  }
};

const MicrosoftSignInButton = ({ thirdPartySignIn, setIsAuthInProgress, isAuthInProgress, isRegistrationInProgress }) => {
  const { instance, inProgress } = useMsal();

  const isLoading = isAuthInProgress || isRegistrationInProgress;

  const environmentNotSet = !microsoftOAuthConfiguration.auth.clientId;

  const renderMicrosoftLogin = () => (
    <ButtonLoader
      variant="outlined"
      messageId="microsoft"
      size="medium"
      onClick={() => {
        setIsAuthInProgress(true);
        handleClick(instance, thirdPartySignIn, setIsAuthInProgress);
      }}
      startIcon={<MicrosoftIcon />}
      disabled={inProgress === InteractionStatus.Startup || environmentNotSet}
      fullWidth
      isLoading={isLoading}
      tooltip={{
        show: environmentNotSet,
        messageId: "signInWithMicrosoftIsNotConfigured"
      }}
    />
  );

  return renderMicrosoftLogin();
};

export default MicrosoftSignInButton;
