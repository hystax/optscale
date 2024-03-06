import { useState } from "react";
import { useQuery } from "@apollo/client";
import Events from "components/Events";
import { GET_EVENTS } from "graphql/api/keeper/queries";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { EVENT_LEVEL } from "utils/constants";
import { scrolledToBottom } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";

const EventsContainer = () => {
  const { organizationId } = useOrganizationInfo();

  const { level, timeStart, timeEnd, lastId } = getQueryParams();

  // Undefined query parameters are ignored in the API calls
  const [requestParams, setRequestParams] = useState({
    level,
    timeStart: timeStart === undefined ? timeStart : Number(timeStart),
    timeEnd: timeEnd === undefined ? timeEnd : Number(timeEnd),
    lastId
  });

  const [events, setEvents] = useState([]);

  const { loading } = useQuery(GET_EVENTS, {
    variables: {
      organizationId,
      requestParams
    },
    onCompleted: (data) => {
      setEvents((state) => [...state, ...(data?.events ?? [])]);
    }
  });

  const applyFilter = (sourceParams) => {
    const { level: newLevel } = sourceParams;

    const params = {
      ...requestParams,
      ...sourceParams,
      // The events API doesn't support the "ALL" level string, so we need to use the "undefined" in order to get a list of all events
      level: newLevel === EVENT_LEVEL.ALL ? undefined : newLevel,
      lastId: undefined
    };
    updateQueryParams(params);
    setRequestParams(params);
    setEvents([]);
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
      }
    }
  };

  return (
    <Events
      eventLevel={requestParams.level}
      events={events}
      isLoading={loading}
      onScroll={handleScroll}
      applyFilter={applyFilter}
    />
  );
};

export default EventsContainer;
