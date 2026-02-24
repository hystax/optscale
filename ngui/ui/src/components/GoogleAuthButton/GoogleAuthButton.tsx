import ButtonLoader from "components/ButtonLoader";
import GoogleIcon from "icons/GoogleIcon";
import { AUTH_PROVIDERS } from "utils/constants";
import { getEnvironmentVariable } from "utils/env";
import { useGoogleLogin } from "./hooks";

const GoogleAuthButton = ({ handleSignIn, isLoading, disabled }) => {
  const clientId = getEnvironmentVariable("VITE_GOOGLE_OAUTH_CLIENT_ID");
  const { login } = useGoogleLogin({
    onSuccess: ({ code: token }) =>
      handleSignIn({ provider: AUTH_PROVIDERS.GOOGLE, token, redirectUri: window.location.origin }),
    onError: (response = {}) => {
      const { message = "", type = "", ...rest } = response;
      console.warn(`Google response failure ${message}: ${type}`, rest);
    },
    clientId,
  });

  const environmentNotSet = !clientId;

  return (
    <ButtonLoader
      variant="outlined"
      messageId="google"
      size="medium"
      onClick={login}
      startIcon={<GoogleIcon />}
      isLoading={isLoading}
      disabled={disabled || environmentNotSet}
      fullWidth
      tooltip={{
        show: environmentNotSet,
        messageId: "signInWithGoogleIsNotConfigured",
      }}
    />
  );
};

export default GoogleAuthButton;
