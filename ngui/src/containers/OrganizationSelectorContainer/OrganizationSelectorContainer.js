import React from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { GET_ORGANIZATIONS } from "api/restapi/actionTypes";
import OrganizationSelector from "components/OrganizationSelector";
import { getMenuItems } from "containers/MainMenuContainer";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { formQueryString, getMenuRootUrl, getQueryParams, removeQueryParam } from "utils/network";
import requestManager from "utils/requestManager";
import { setScopeId } from "./actionCreators";
import { SCOPE_ID } from "./reducer";

const OrganizationSelectorContainer = () => {
  const dispatch = useDispatch();
  const {
    apiData: { organizations }
  } = useApiData(GET_ORGANIZATIONS);

  const { isLoading } = useApiState(GET_ORGANIZATIONS);

  const { organizationId, organizationPoolId } = useOrganizationInfo();

  const navigate = useNavigate();

  const handleScopeChange = (scopeId) => {
    requestManager.cancelAllPendingRequests();

    removeQueryParam(SCOPE_ID);

    const menu = getMenuItems(organizationPoolId);

    // The straightforward solution to persist query parameters when changing the organization
    // More context:
    // * https://gitlab.com/hystax/ngui/-/merge_requests/2773
    // * https://datatrendstech.atlassian.net/browse/OS-4786
    const { type } = getQueryParams();

    const to = [getMenuRootUrl(menu), formQueryString({ type })].join("?");

    navigate(to);

    dispatch(setScopeId(scopeId));
  };

  return (
    <OrganizationSelector
      organizations={organizations}
      organizationId={organizationId}
      onChange={handleScopeChange}
      isLoading={isLoading}
    />
  );
};

export default OrganizationSelectorContainer;
