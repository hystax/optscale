import React from "react";
import { useLocation } from "react-router-dom";
import { GET_TOKEN } from "api/auth/actionTypes";
import { GET_ORGANIZATIONS, GET_INVITATIONS } from "api/restapi/actionTypes";
import Greeter from "components/Greeter";
import LoginForm from "components/LoginForm";
import Redirector from "components/Redirector";
import RegistrationForm from "components/RegistrationForm";
import { useApiData } from "hooks/useApiData";
import { useNewAuthorization } from "hooks/useNewAuthorization";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { HOME_FIRST_TIME, HOME, ACCEPT_INVITATIONS, REGISTER, LOGIN } from "urls";
import { isEmpty } from "utils/arrays";
import { getQueryParams } from "utils/network";

const AuthorizationContainer = () => {
  const { pathname } = useLocation();

  const {
    apiData: { organizations }
  } = useApiData(GET_ORGANIZATIONS, []);

  const { apiData: invitations } = useApiData(GET_INVITATIONS, []);

  const { isDemo } = useOrganizationInfo();

  const {
    apiData: { token }
  } = useApiData(GET_TOKEN);

  const {
    authorize,
    register,
    isCreateUserLoading,
    isGetOrganizationsLoading,
    isGetOrganizationsDataReady,
    isGetInvitationsLoading,
    isGetInvitationsDataReady,
    isCreateOrganizationLoading,
    isSignInLoading,
    isGetTokenLoading
  } = useNewAuthorization({
    onSuccessRedirectionPath: pathname === REGISTER ? HOME_FIRST_TIME : undefined
  });

  const onSubmitRegister = ({ name, email, password }) => {
    register(name, email, password);
  };

  const onSubmitLogin = ({ email, password }) => {
    authorize(email, password);
  };

  // isGetTokenLoading used for LoginForm, isCreateUserLoading for RegistrationForm
  const isLoading =
    isGetOrganizationsLoading ||
    isGetInvitationsLoading ||
    isCreateOrganizationLoading ||
    isSignInLoading ||
    isGetTokenLoading ||
    isCreateUserLoading;

  const { invited: queryInvited, next = HOME } = getQueryParams();
  const isInvited = queryInvited !== undefined;

  const createForm =
    {
      [LOGIN]: () => <LoginForm onSubmit={onSubmitLogin} isLoading={isLoading} isInvited={isInvited} />,
      [REGISTER]: () => <RegistrationForm onSubmit={onSubmitRegister} isLoading={isLoading} isInvited={isInvited} />
    }[pathname] || (() => null);

  const hasInvitations = !isEmpty(invitations);
  const hasOrganizations = !isEmpty(organizations);

  // First redirect condition ("after authorization"):
  // We can proceed to "next" (usually home) page or accept invitations only when:
  // 1) got token and invitations
  // AND
  // 2) invitations are not empty OR we are not in demo and have organizations
  // Last part means we already loaded organizations or created one.
  // It is required here, due to after redirect there are different containers which work with organization-dependant api calls
  // and they all will fail before hook will create organization or load existing
  const redirectAfterAuthorization =
    Boolean(token) && isGetInvitationsDataReady && (hasInvitations || (!isDemo && hasOrganizations));

  // Second redirect condition: for authorized user on /login or /register url
  // Works if there is a token, but nothing is loading and organizations api call did not made (!isGetOrganizationsDataReady)
  const redirectForAuthorizedUsers =
    Boolean(token) && !isLoading && !isGetOrganizationsDataReady && !isGetInvitationsDataReady && !isDemo;

  const redirectPath = hasInvitations ? ACCEPT_INVITATIONS : next;

  return (
    <Redirector condition={redirectAfterAuthorization || redirectForAuthorizedUsers} to={redirectPath}>
      <Greeter form={createForm()} />
    </Redirector>
  );
};

export default AuthorizationContainer;
