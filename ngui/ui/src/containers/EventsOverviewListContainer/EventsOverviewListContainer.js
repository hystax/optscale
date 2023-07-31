import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getLatestEvents } from "api/keeper/actionCreators";
import { GET_LATEST_EVENTS } from "api/keeper/actionTypes";
import EventsOverviewList from "components/EventsOverviewList";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const EventsOverviewListContainer = () => {
  const { organizationId } = useOrganizationInfo();
  const {
    apiData: { events = [] }
  } = useApiData(GET_LATEST_EVENTS);
  const { isLoading, shouldInvoke } = useApiState(GET_LATEST_EVENTS);

  const dispatch = useDispatch();

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getLatestEvents(organizationId));
    }
  }, [dispatch, shouldInvoke, organizationId]);

  return <EventsOverviewList events={events} isLoading={isLoading} />;
};

export default EventsOverviewListContainer;
