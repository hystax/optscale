import React from "react";
import PropTypes from "prop-types";
import { GoogleLogin } from "react-google-login";
import ButtonLoader from "components/ButtonLoader";
import { PROVIDERS } from "hooks/useNewAuthorization";
import GoogleIcon from "icons/GoogleIcon";

const failureResponseGoogle = (response = {}) => {
  const { error = "", details = "" } = response;
  console.log(`Google response failure ${error}: ${details}`);
};

const handleSuccessResponse = ({ tokenId }, callback) => {
  callback(PROVIDERS.GOOGLE, { token: tokenId });
};

const GoogleAuthButton = ({
  options = {},
  thirdPartySignIn,
  setIsAuthInProgress,
  isAuthInProgress,
  isRegistrationInProgress
}) => {
  const { theme = "dark" } = options;

  const isLoading = isAuthInProgress || isRegistrationInProgress;

  const renderGoogleLogin = () => (
    <GoogleLogin
      clientId={process.env.REACT_APP_GOOGLE_OAUTH_CLIENT_ID}
      onSuccess={(response) => handleSuccessResponse(response, thirdPartySignIn)}
      onFailure={() => {
        setIsAuthInProgress(false);
        failureResponseGoogle();
      }}
      theme={theme}
      render={(renderProps) => (
        <ButtonLoader
          variant="outlined"
          messageId="google"
          size="medium"
          onClick={() => {
            setIsAuthInProgress(true);
            renderProps.onClick();
          }}
          disabled={renderProps.disabled}
          startIcon={<GoogleIcon />}
          isLoading={isLoading}
          fullWidth
        />
      )}
    />
  );

  return renderGoogleLogin();
};

GoogleAuthButton.propTypes = {
  options: PropTypes.object,
  thirdPartySignIn: PropTypes.func.isRequired,
  setIsAuthInProgress: PropTypes.func.isRequired,
  isAuthInProgress: PropTypes.bool.isRequired,
  isRegistrationInProgress: PropTypes.bool.isRequired
};

export default GoogleAuthButton;
