import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { getEvents } from "api";
import { GET_EVENTS } from "api/keeper/actionTypes";
import Events from "components/Events";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useInitialMount } from "hooks/useInitialMount";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isEmpty } from "utils/arrays";
import { EVENT_LEVEL } from "utils/constants";
import { scrolledToBottom } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";

const EventsContainer = () => {
  const { organizationId } = useOrganizationInfo();
  const {
    apiData: { events: eventsApiData = [] }
  } = useApiData(GET_EVENTS);

  const { level, timeStart, timeEnd, lastId } = getQueryParams();

  const [requestParams, setRequestParams] = useState({
    level: Object.values(EVENT_LEVEL).includes(level) ? level : undefined,
    timeStart,
    timeEnd,
    lastId
  });

  const [events, setEvents] = useState([]);

  const { isLoading, shouldInvoke } = useApiState(GET_EVENTS, { ...requestParams, organizationId });

  const dispatch = useDispatch();

  const { isInitialMount, setIsInitialMount } = useInitialMount();

  useEffect(() => {
    if (!isEmpty(eventsApiData)) {
      setEvents((state) => [...state, ...eventsApiData]);
    }
  }, [eventsApiData]);

  useEffect(() => {
    if (isInitialMount && shouldInvoke) {
      setIsInitialMount(false);
      setEvents([]);
      dispatch(getEvents(organizationId, requestParams));
    }
  }, [dispatch, shouldInvoke, requestParams, organizationId, isInitialMount, setIsInitialMount]);

  const applyFilter = (sourceParams) => {
    const params = {
      ...requestParams,
      ...sourceParams,
      lastId: undefined
    };
    updateQueryParams(params);
    setRequestParams(params);
    setEvents([]);
    dispatch(getEvents(organizationId, params));
  };

  const handleScroll = (event) => {
    if (scrolledToBottom(event.target)) {
      const { [events.length - 1]: lastEvent } = events;
      // While requesting, the scroll listener remains active, preventing from sending a new request with the same last_id
      if (lastEvent !== undefined && lastEvent.id !== requestParams.lastId) {
        const params = {
          ...requestParams,
          lastId: lastEvent.id
        };
        setRequestParams(params);
        updateQueryParams(params);
        dispatch(getEvents(organizationId, params));
      }
    }
  };

  return (
    <Events
      eventLevel={requestParams.level}
      events={events}
      isLoading={isLoading}
      onScroll={handleScroll}
      applyFilter={applyFilter}
    />
  );
};

export default EventsContainer;
