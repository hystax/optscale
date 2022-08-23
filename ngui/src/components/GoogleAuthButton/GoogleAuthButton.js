import React from "react";
import PropTypes from "prop-types";
import { GoogleLogin } from "react-google-login";
import ButtonLoader from "components/ButtonLoader";
import { useNewAuthorization, PROVIDERS } from "hooks/useNewAuthorization";
import GoogleIcon from "icons/GoogleIcon";

const failureResponseGoogle = (response) => {
  const { error = "", details = "" } = response;
  console.log(`${error}: ${details}`);
};

const handleSuccessResponse = ({ tokenId }, callback) => {
  callback(PROVIDERS.GOOGLE, { token: tokenId });
};

const GoogleAuthButton = ({ options = {} }) => {
  const { theme = "dark" } = options;

  const {
    thirdPartySignIn,
    isGetTokenLoading,
    isGetOrganizationsLoading,
    isGetInvitationsLoading,
    isCreateOrganizationLoading,
    isSignInLoading
  } = useNewAuthorization();

  const isLoading =
    isGetTokenLoading || isGetOrganizationsLoading || isGetInvitationsLoading || isSignInLoading || isCreateOrganizationLoading;

  const renderGoogleLogin = () => (
    <GoogleLogin
      clientId={process.env.REACT_APP_GOOGLE_OAUTH_CLIENT_ID}
      onSuccess={(response) => handleSuccessResponse(response, thirdPartySignIn)}
      onFailure={failureResponseGoogle}
      theme={theme}
      render={(renderProps) => (
        <ButtonLoader
          variant="outlined"
          messageId="google"
          size="medium"
          onClick={renderProps.onClick}
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
  options: PropTypes.object
};

export default GoogleAuthButton;
