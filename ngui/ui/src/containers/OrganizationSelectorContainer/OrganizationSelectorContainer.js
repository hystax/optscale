import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { GET_ORGANIZATIONS } from "api/restapi/actionTypes";
import OrganizationSelector from "components/OrganizationSelector";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { formQueryString, getMenuRootUrl, getQueryParams, removeQueryParam } from "utils/network";
import requestManager from "utils/requestManager";
import { setScopeId } from "./actionCreators";
import { SCOPE_ID } from "./reducer";

const OrganizationSelectorContainer = ({ mainMenu }) => {
  const dispatch = useDispatch();
  const {
    apiData: { organizations }
  } = useApiData(GET_ORGANIZATIONS);

  const { isLoading } = useApiState(GET_ORGANIZATIONS);

  const { organizationId } = useOrganizationInfo();

  const navigate = useNavigate();

  const handleScopeChange = (scopeId) => {
    requestManager.cancelAllPendingRequests();
    removeQueryParam(SCOPE_ID);

    // The straightforward solution to persist query parameters when changing the organization
    // More context:
    // * https://gitlab.com/hystax/ngui/-/merge_requests/2773
    // * https://datatrendstech.atlassian.net/browse/OS-4786
    const { type } = getQueryParams();

    const to = [getMenuRootUrl(mainMenu), formQueryString({ type })].join("?");

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

OrganizationSelectorContainer.propTypes = {
  mainMenu: PropTypes.array.isRequired
};

export default OrganizationSelectorContainer;
