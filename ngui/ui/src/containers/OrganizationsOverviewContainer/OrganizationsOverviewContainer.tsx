import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getOrganizationsOverview } from "api";
import { GET_ORGANIZATIONS_OVERVIEW } from "api/restapi/actionTypes";
import OrganizationsOverview from "components/OrganizationsOverview";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

const OrganizationsOverviewContainer = () => {
  const {
    apiData: { organizations = [] }
  } = useApiData(GET_ORGANIZATIONS_OVERVIEW);

  const { isLoading, shouldInvoke } = useApiState(GET_ORGANIZATIONS_OVERVIEW, { details: true });
  const dispatch = useDispatch();

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOrganizationsOverview());
    }
  }, [shouldInvoke, dispatch]);

  return <OrganizationsOverview data={organizations} isLoading={isLoading} />;
};

export default OrganizationsOverviewContainer;
