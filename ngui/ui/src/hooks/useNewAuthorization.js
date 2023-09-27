import { useCallback, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { getToken, getOrganizations, getInvitations, createOrganization, signIn, createUser, AUTH, RESTAPI } from "api";
import { GET_TOKEN, SIGN_IN, CREATE_USER } from "api/auth/actionTypes";
import { GET_ORGANIZATIONS, GET_INVITATIONS, CREATE_ORGANIZATION } from "api/restapi/actionTypes";
import { setScopeId } from "containers/OrganizationSelectorContainer/actionCreators";
import { SCOPE_ID } from "containers/OrganizationSelectorContainer/reducer";
import { ACCEPT_INVITATIONS, HOME } from "urls";
import { trackEvent, GA_EVENT_CATEGORIES } from "utils/analytics";
import { checkError } from "utils/api";
import { isEmpty } from "utils/arrays";
import { getQueryParams } from "utils/network";
import { useApiState } from "./useApiState";

export const PROVIDERS = Object.freeze({
  GOOGLE: "google",
  MICROSOFT: "microsoft"
});

// TODO - after Live Demo auth is updated:
// - remove useAuthorization and rename this one
// - refactor/generalize

export const useNewAuthorization = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const [isAuthInProgress, setIsAuthInProgress] = useState(false);
  const [isRegistrationInProgress, setIsRegistrationInProgress] = useState(false);

  const { isLoading: isGetTokenLoading } = useApiState(GET_TOKEN);
  const { isLoading: isGetInvitationsLoading, isDataReady: isGetInvitationsDataReady } = useApiState(GET_INVITATIONS);
  const { isLoading: isGetOrganizationsLoading, isDataReady: isGetOrganizationsDataReady } = useApiState(GET_ORGANIZATIONS);
  const { isLoading: isCreateOrganizationLoading } = useApiState(CREATE_ORGANIZATION);
  const { isLoading: isCreateUserLoading } = useApiState(CREATE_USER);
  const { isLoading: isSignInLoading } = useApiState(SIGN_IN);

  const redirectOnSuccess = useCallback(
    (to) => {
      navigate(to);
    },
    [navigate]
  );

  const updateScopeId = useCallback(
    (currentState) => {
      const { [SCOPE_ID]: organizationIdQueryParam } = getQueryParams();
      const { organizations = [] } = currentState.restapi[GET_ORGANIZATIONS];
      const { organizationId: currentOrganizationId } = currentState;
      const targetOrganizationId = organizationIdQueryParam || currentOrganizationId;

      if (organizations.find((organization) => organization.id === targetOrganizationId)) {
        dispatch(setScopeId(targetOrganizationId));
        return Promise.resolve();
      }

      dispatch(setScopeId(organizations[0]?.id));
      return Promise.resolve();
    },
    [dispatch]
  );

  const activateScope = useCallback(
    (email, { getOnSuccessRedirectionPath } = {}) =>
      dispatch((_, getState) =>
        dispatch(getOrganizations())
          .then(() => checkError(GET_ORGANIZATIONS, getState()))
          .then(() => dispatch(getOrganizations()))
          .then(() => getState()?.[RESTAPI]?.[GET_ORGANIZATIONS]?.organizations)
          .then((existingOrganizations) => {
            if (isEmpty(existingOrganizations)) {
              return dispatch(createOrganization(`${email}'s Organization`))
                .then(() => checkError(CREATE_ORGANIZATION, getState()))
                .then(() => dispatch(getOrganizations()))
                .then(() => checkError(GET_ORGANIZATIONS, getState()));
            }
            return undefined;
          })
          .then(() => updateScopeId(getState()))
          .then(() => {
            const redirectPath =
              typeof getOnSuccessRedirectionPath === "function"
                ? getOnSuccessRedirectionPath({ userEmail: email })
                : getQueryParams().next || HOME;

            return redirectOnSuccess(redirectPath);
          })
          .then(() => {
            const { register, provider } = getState()?.[AUTH]?.[GET_TOKEN] ?? {};
            if (register) {
              Promise.resolve(trackEvent({ category: GA_EVENT_CATEGORIES.USER, action: "Registered", label: provider }));
            }
          })
          .catch(() => Promise.reject())
          .finally(() => {
            setIsAuthInProgress(false);
            setIsRegistrationInProgress(false);
          })
      ),
    [dispatch, redirectOnSuccess, updateScopeId]
  );

  const authorize = useCallback(
    ({ email, password }, { getOnSuccessRedirectionPath }) => {
      setIsAuthInProgress(true);
      dispatch((_, getState) =>
        dispatch(getToken(email, password))
          .then(() => checkError(GET_TOKEN, getState()))
          .then(() => dispatch(getInvitations()))
          .then(() => checkError(GET_INVITATIONS, getState()))
          .then(() => getState()?.[RESTAPI]?.[GET_INVITATIONS])
          .then((pendingInvitations) => {
            if (isEmpty(pendingInvitations)) {
              const { userEmail } = getState()?.[AUTH]?.[GET_TOKEN] ?? {};
              Promise.resolve(activateScope(userEmail, { getOnSuccessRedirectionPath }));
            } else {
              navigate(ACCEPT_INVITATIONS);
            }
          })
          .catch(() => {
            setIsAuthInProgress(false);
          })
      );
    },
    [dispatch, activateScope, navigate]
  );

  const register = useCallback(
    ({ name, email, password }, { getOnSuccessRedirectionPath }) => {
      setIsRegistrationInProgress(true);
      dispatch((_, getState) =>
        dispatch(createUser(name, email, password))
          .then(() => checkError(CREATE_USER, getState()))
          .then(() => dispatch(getInvitations()))
          .then(() => checkError(GET_INVITATIONS, getState()))
          .then(() => getState()?.[RESTAPI]?.[GET_INVITATIONS])
          .then((pendingInvitations) => {
            if (isEmpty(pendingInvitations)) {
              const { userEmail } = getState()?.[AUTH]?.[GET_TOKEN] ?? {};
              Promise.resolve(activateScope(userEmail, { getOnSuccessRedirectionPath }));
            } else {
              navigate(ACCEPT_INVITATIONS);
            }
          })
          .catch(() => {
            setIsRegistrationInProgress(false);
          })
      );
    },
    [dispatch, activateScope, navigate]
  );

  const thirdPartySignIn = useCallback(
    ({ provider, params }, { getOnSuccessRedirectionPath }) => {
      setIsAuthInProgress(true);
      dispatch((_, getState) =>
        dispatch(signIn(provider, params))
          .then(() => checkError(SIGN_IN, getState()))
          .then(() => dispatch(getInvitations()))
          .then(() => checkError(GET_INVITATIONS, getState()))
          .then(() => getState()?.[RESTAPI]?.[GET_INVITATIONS])
          .then((pendingInvitations) => {
            if (isEmpty(pendingInvitations)) {
              const useEmail = getState()?.[AUTH]?.[GET_TOKEN]?.userEmail;
              Promise.resolve(activateScope(useEmail, { getOnSuccessRedirectionPath }));
            } else {
              navigate(ACCEPT_INVITATIONS);
            }
          })
          .catch(() => {
            setIsAuthInProgress(false);
          })
      );
    },
    [dispatch, activateScope, navigate]
  );

  return {
    authorize,
    register,
    thirdPartySignIn,
    setIsAuthInProgress,
    isGetTokenLoading,
    isGetOrganizationsLoading,
    isGetInvitationsLoading,
    isGetInvitationsDataReady,
    isCreateOrganizationLoading,
    isCreateUserLoading,
    isSignInLoading,
    isGetOrganizationsDataReady,
    activateScope,
    isAuthInProgress,
    isRegistrationInProgress
  };
};
