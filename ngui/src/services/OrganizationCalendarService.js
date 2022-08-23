import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getOrganizationCalendar } from "api";
import { GET_ORGANIZATION_CALENDAR } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

export const useGet = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { apiData: organizationCalendar = {} } = useApiData(GET_ORGANIZATION_CALENDAR);

  const { isLoading, shouldInvoke } = useApiState(GET_ORGANIZATION_CALENDAR, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOrganizationCalendar(organizationId));
    }
  }, [shouldInvoke, dispatch, organizationId]);

  return { isLoading, organizationCalendar };
};

function OrganizationCalendarService() {
  return { useGet };
}

export default OrganizationCalendarService;
