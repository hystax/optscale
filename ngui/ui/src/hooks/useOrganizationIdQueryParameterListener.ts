import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { GET_ORGANIZATIONS } from "api/restapi/actionTypes";
import { setScopeId } from "containers/OrganizationSelectorContainer/actionCreators";
import { getQueryParams } from "utils/network";
import { useApiData } from "./useApiData";

const ORGANIZATION_ID_QUERY_PARAMETER_NAME = "organizationId";

export const useOrganizationIdQueryParameterListener = () => {
  const { [ORGANIZATION_ID_QUERY_PARAMETER_NAME]: organizationIdQueryParameter } = getQueryParams();
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
