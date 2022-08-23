import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getEnvironmentBookings } from "api";
import { GET_RESOURCE_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { GET_ENVIRONMENT_BOOKINGS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

const useGet = (resourceId) => {
  const dispatch = useDispatch();

  const { apiData: bookings } = useApiData(GET_ENVIRONMENT_BOOKINGS, []);

  const { isLoading: isGetEnvironmentBookingsLoading, shouldInvoke } = useApiState(GET_ENVIRONMENT_BOOKINGS, resourceId);
  const { isLoading: isGetResourceAllowedActionsLoading } = useApiState(GET_RESOURCE_ALLOWED_ACTIONS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getEnvironmentBookings(resourceId));
    }
  }, [dispatch, resourceId, shouldInvoke]);

  return { isGetEnvironmentBookingsLoading, isGetResourceAllowedActionsLoading, bookings };
};

function EnvironmentBookingsService() {
  return { useGet };
}

export default EnvironmentBookingsService;
