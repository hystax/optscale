import React, { useCallback, useEffect, useRef, useState } from "react";
import { SECOND } from "api/constants";
import Events from "components/Events";
import { useEventsLazyQuery } from "graphql/__generated__/hooks/keeper";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getLastElement } from "utils/arrays";
import { EVENT_LEVEL, EVENTS_LIMIT } from "utils/constants";
import { scrolledToBottom } from "utils/layouts";
import { getSearchParams, updateSearchParams } from "utils/network";

type FilterParams = {
  level: keyof typeof EVENT_LEVEL;
  timeStart?: number;
  timeEnd?: number;
  descriptionLike?: string;
  lastId?: string;
  includeDebugEvents?: boolean;
};

type FilterNames = keyof FilterParams;

type RequestParams = {
  time_start?: number;
  time_end?: number;
  description_like?: string;
  last_id?: string;
  level: Exclude<FilterParams["level"], typeof EVENT_LEVEL.ALL>[];
  limit?: number;
};

type Variables = {
  organizationId: string;
  requestParams: RequestParams;
};

const POLL_INTERVAL = 10 * SECOND;

const getQueryParamFilters = () => {
  const {
    level = EVENT_LEVEL.ALL,
    timeStart,
    timeEnd,
    descriptionLike = "",
    includeDebugEvents = false,
  } = getSearchParams() as Partial<FilterParams>;

  return {
    level,
    timeStart: timeStart === undefined ? timeStart : Number(timeStart),
    timeEnd: timeEnd === undefined ? timeEnd : Number(timeEnd),
    descriptionLike,
    includeDebugEvents,
  };
};

/**
 * Request Flows:
 *
 * 1. Initial data:
 *    - Fetches events on component mount using default or query param filters.
 *    - Starts polling for periodic updates.
 *
 * 2. Filter changes:
 *    - Aborts ongoing requests and resets polling.
 *    - Fetches filtered events and replaces the current list.
 *    - Resumes polling with the updated filters.
 *
 * 3. Pagination:
 *    - Fetches additional events when scrolled to the bottom.
 *    - Appends new events to the current list without interrupting polling.
 *
 * 4. Concurrency management:
 *    - Properly aborts ongoing requests during filter changes or pagination.
 *    - Prevents redundant or conflicting requests to ensure data consistency.
 */
const EventsContainer = () => {
  const { organizationId } = useOrganizationInfo();

  const [filters, setFilters] = useState<FilterParams>(() => getQueryParamFilters());

  const getQueryVariables = useCallback(
    (params: FilterParams): Variables => {
      const getLevelParameter = () => {
        const levels =
          params.level === EVENT_LEVEL.ALL ? [EVENT_LEVEL.INFO, EVENT_LEVEL.WARNING, EVENT_LEVEL.ERROR] : [params.level];

        return params.includeDebugEvents ? [...levels, EVENT_LEVEL.DEBUG] : levels;
      };

      return {
        organizationId,
        requestParams: {
          time_start: params.timeStart,
          time_end: params.timeEnd,
          last_id: params.lastId,
          description_like: params.descriptionLike,
          limit: EVENTS_LIMIT,
          level: getLevelParameter(),
        },
      };
    },
    [organizationId]
  );

  const intervalId = useRef();

  const [events, setEvents] = useState([]);

  const getEventsAbortControllerRef = useRef<AbortController | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [getEvents] = useEventsLazyQuery({
    fetchPolicy: "no-cache",
  });

  const refetchAbortControllerRef = useRef<AbortController | null>(null);
  const [refetchEvents] = useEventsLazyQuery({
    fetchPolicy: "no-cache",
  });

  const fetchMoreAbortControllerRef = useRef<AbortController | null>(null);
  const [isFetchingMore, setIsFetchingMore] = useState(false);
  const [fetchMoreEvents] = useEventsLazyQuery({
    fetchPolicy: "no-cache",
  });

  const refetch = useCallback(
    (variables: Variables) => {
      refetchAbortControllerRef.current = new AbortController();

      refetchEvents({
        variables,
        context: {
          fetchOptions: {
            signal: refetchAbortControllerRef.current?.signal,
          },
        },
      }).then(({ data }) => {
        if (data) {
          setEvents((currentEvents) => {
            /**
             * If more than EVENTS_LIMIT events are generated between poll intervals,
             * only the latest EVENTS_LIMIT events will be displayed, and older excess events will be lost.
             */
            const firstEvents = currentEvents.slice(0, EVENTS_LIMIT);
            const newEvents = data.events.filter((event) => !firstEvents.some((currentEvent) => currentEvent.id === event.id));
            return [...newEvents, ...currentEvents];
          });
        }
      });
    },
    [refetchEvents]
  );

  const setPolling = useCallback(
    (variables: Variables) => {
      if (!intervalId.current) {
        intervalId.current = setInterval(() => {
          refetch(variables);
        }, POLL_INTERVAL);
      }
    },
    [refetch]
  );

  const resetPolling = () => {
    clearInterval(intervalId.current);
    intervalId.current = undefined;
  };

  useEffect(() => {
    const variables = getQueryVariables(getQueryParamFilters());

    setIsLoading(true);

    getEvents({
      variables,
    })
      .then(({ data }) => {
        setEvents(data.events);
        setPolling(variables);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [getEvents, getQueryVariables, setPolling]);

  useEffect(
    () => () => {
      resetPolling();
    },
    []
  );

  const applyFilter = (newFilterParams: FilterParams) => {
    const filterParams: FilterParams = {
      level: newFilterParams.level ?? filters.level,
      timeStart: newFilterParams.timeStart ?? filters.timeStart,
      timeEnd: newFilterParams.timeEnd ?? filters.timeEnd,
      descriptionLike: newFilterParams.descriptionLike ?? filters.descriptionLike,
      includeDebugEvents: newFilterParams.includeDebugEvents ?? filters.includeDebugEvents,
    };

    const areFiltersDifferent = (Object.keys(filterParams) as FilterNames[]).some((key) => filterParams[key] !== filters[key]);

    if (areFiltersDifferent) {
      updateSearchParams(filterParams);

      setFilters((currentRequestParams) => ({
        ...currentRequestParams,
        ...filterParams,
      }));

      const variables = getQueryVariables(filterParams);

      if (refetchAbortControllerRef.current) {
        refetchAbortControllerRef.current.abort("Abort refetch events");
      }
      if (fetchMoreAbortControllerRef.current) {
        fetchMoreAbortControllerRef.current.abort("Abort fetch more events");
      }
      if (getEventsAbortControllerRef.current) {
        getEventsAbortControllerRef.current.abort("Aborting get events");
      }
      getEventsAbortControllerRef.current = new AbortController();

      resetPolling();

      setIsLoading(true);

      getEvents({
        variables,
        context: {
          fetchOptions: {
            signal: getEventsAbortControllerRef.current?.signal,
          },
        },
      })
        .then(({ data }) => {
          setEvents(data.events);
          setPolling(variables);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  };

  const handleScroll = (event: React.UIEvent<HTMLDivElement, UIEvent>) => {
    if (isFetchingMore) {
      return;
    }

    if (scrolledToBottom(event.target)) {
      const lastEvent = getLastElement(events);

      fetchMoreAbortControllerRef.current = new AbortController();

      setIsFetchingMore(true);

      fetchMoreEvents({
        variables: getQueryVariables({
          ...filters,
          lastId: lastEvent.id,
        }),
        context: {
          fetchOptions: {
            signal: fetchMoreAbortControllerRef.current?.signal,
          },
        },
      })
        .then(({ data }) => {
          if (data) {
            setEvents((currentEvents) => [...currentEvents, ...data.events]);
          }
        })
        .finally(() => {
          setIsFetchingMore(false);
        });
    }
  };

  return (
    <Events
      eventLevel={filters.level}
      descriptionLike={filters.descriptionLike}
      includeDebugEvents={filters.includeDebugEvents}
      events={events}
      isLoading={isLoading}
      isFetchingMore={isFetchingMore}
      onScroll={handleScroll}
      applyFilter={applyFilter}
    />
  );
};

export default EventsContainer;
