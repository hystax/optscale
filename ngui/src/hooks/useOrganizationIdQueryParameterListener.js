import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { GET_ORGANIZATIONS } from "api/restapi/actionTypes";
import { setScopeId } from "containers/OrganizationSelectorContainer/actionCreators";
import { getQueryParams } from "utils/network";
import { useApiData } from "./useApiData";

export const useOrganizationIdQueryParameterListener = () => {
  const { organizationId: organizationIdQueryParameter } = getQueryParams();
  const dispatch = useDispatch();

  const {
    apiData: { organizations = [] }
  } = useApiData(GET_ORGANIZATIONS);

  useEffect(() => {
    if (
      organizationIdQueryParameter &&
      organizations.find((organization) => organization.id === organizationIdQueryParameter)
    ) {
      dispatch(setScopeId(organizationIdQueryParameter));
    }
  }, [dispatch, organizationIdQueryParameter, organizations]);
};
