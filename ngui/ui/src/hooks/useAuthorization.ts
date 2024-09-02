import { useCallback } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { getToken, getOrganizations } from "api";
import { GET_TOKEN } from "api/auth/actionTypes";
import { GET_ORGANIZATIONS } from "api/restapi/actionTypes";
import { setScopeId } from "containers/OrganizationSelectorContainer/actionCreators";
import { SCOPE_ID } from "containers/OrganizationSelectorContainer/reducer";
import { checkError } from "utils/api";
import { getQueryParams } from "utils/network";
import { useApiState } from "./useApiState";

export const useAuthorization = ({ onSuccessRedirectionPath } = {}) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const { isLoading: isGetTokenLoading } = useApiState(GET_TOKEN);
  const { isLoading: isGetOrganizationLoading } = useApiState(GET_ORGANIZATIONS);

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

  const authorize = useCallback(
    (email, password) =>
      dispatch((_, getState) =>
        dispatch(getToken({ email, password }))
          .then(() => checkError(GET_TOKEN, getState()))
          .then(() => dispatch(getOrganizations()))
          .then(() => checkError(GET_ORGANIZATIONS, getState()))
          .then(() => updateScopeId(getState()))
          .then(() => {
            if (onSuccessRedirectionPath) {
              navigate(onSuccessRedirectionPath);
            }
            return Promise.resolve();
          })
          // Return rejection since this chain can be part of another chain => reject entire chain if something went wrong here
          .catch(() => Promise.reject())
      ),
    [dispatch, navigate, onSuccessRedirectionPath, updateScopeId]
  );

  return {
    authorize,
    isLoading: isGetTokenLoading || isGetOrganizationLoading
  };
};
