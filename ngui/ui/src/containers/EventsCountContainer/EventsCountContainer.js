import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getEventsCount } from "api";
import { GET_EVENTS_COUNT } from "api/keeper/actionTypes";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const EventsCountContainer = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { shouldInvoke } = useApiState(GET_EVENTS_COUNT, organizationId);

  useEffect(() => {
    if (organizationId && shouldInvoke) {
      dispatch(getEventsCount(organizationId));
    }
  }, [shouldInvoke, dispatch, organizationId]);

  return null;
};

export default EventsCountContainer;
