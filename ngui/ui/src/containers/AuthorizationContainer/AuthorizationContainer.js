import React from "react";
import { useLocation } from "react-router-dom";
import { GET_TOKEN } from "api/auth/actionTypes";
import GoogleAuthButton from "components/GoogleAuthButton";
import Greeter from "components/Greeter";
import LoginForm from "components/LoginForm";
import MicrosoftSignInButton from "components/MicrosoftSignInButton";
import OAuthSignIn from "components/OAuthSignIn";
import Redirector from "components/Redirector";
import RegistrationForm from "components/RegistrationForm";
import TopAlertWrapper from "components/TopAlertWrapper";
import { ALERT_TYPES } from "components/TopAlertWrapper/TopAlertWrapper";
import { useApiData } from "hooks/useApiData";
import { useNewAuthorization } from "hooks/useNewAuthorization";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { HOME_FIRST_TIME, HOME, REGISTER, LOGIN } from "urls";
import { getQueryParams } from "utils/network";

const AuthorizationContainer = () => {
  const { pathname } = useLocation();

  const { invited: queryInvited, next = HOME, userEmail: userEmailQueryParameter } = getQueryParams();

  const { authorize, register, isRegistrationInProgress, isAuthInProgress, thirdPartySignIn, setIsAuthInProgress } =
    useNewAuthorization();

  const { isDemo } = useOrganizationInfo();
  const {
    apiData: { token }
  } = useApiData(GET_TOKEN);
  const isTokenExists = Boolean(token);

  const onSubmitRegister = ({ name, email, password }) => {
    register(
      { name, email, password },
      {
        getOnSuccessRedirectionPath: () => HOME_FIRST_TIME
      }
    );
  };

  const getLoginSuccessRedirectionPath = ({ userEmail }) => (userEmailQueryParameter === userEmail ? next : HOME);

  const onSubmitLogin = ({ email, password }) => {
    authorize(
      { email, password },
      {
        getOnSuccessRedirectionPath: getLoginSuccessRedirectionPath
      }
    );
  };

  const onThirdPartySignIn = (provider, params) =>
    thirdPartySignIn(
      { provider, params },
      {
        getOnSuccessRedirectionPath: getLoginSuccessRedirectionPath
      }
    );

  // isGetTokenLoading used for LoginForm, isCreateUserLoading for RegistrationForm
  const isLoading = isRegistrationInProgress || isAuthInProgress;

  const isInvited = queryInvited !== undefined;

  const createForm =
    {
      [LOGIN]: () => <LoginForm onSubmit={onSubmitLogin} isLoading={isLoading} isInvited={isInvited} />,
      [REGISTER]: () => <RegistrationForm onSubmit={onSubmitRegister} isLoading={isLoading} isInvited={isInvited} />
    }[pathname] || (() => null);

  // redirecting already authorized user from /login and /register pages
  const shouldRedirectAuthorizedUser = !isAuthInProgress && !isRegistrationInProgress && !isDemo && isTokenExists;

  return (
    <Redirector condition={shouldRedirectAuthorizedUser} to={next}>
      <TopAlertWrapper blacklistIds={[ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING, ALERT_TYPES.DATA_SOURCES_PROCEEDED]} />
      <Greeter
        form={createForm()}
        oAuthForm={
          <OAuthSignIn
            googleButton={
              <GoogleAuthButton
                thirdPartySignIn={onThirdPartySignIn}
                setIsAuthInProgress={setIsAuthInProgress}
                isAuthInProgress={isAuthInProgress}
                isRegistrationInProgress={isRegistrationInProgress}
              />
            }
            microsoftButton={
              <MicrosoftSignInButton
                thirdPartySignIn={onThirdPartySignIn}
                setIsAuthInProgress={setIsAuthInProgress}
                isAuthInProgress={isAuthInProgress}
                isRegistrationInProgress={isRegistrationInProgress}
              />
            }
          />
        }
      />
    </Redirector>
  );
};

export default AuthorizationContainer;
