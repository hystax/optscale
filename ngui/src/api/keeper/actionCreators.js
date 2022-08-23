import { handleSuccess } from "api/actionCreators";
import { MINUTE } from "api/constants";
import { apiAction, getApiUrl, hashParams } from "api/utils";
import {
  GET_EVENTS,
  GET_EVENTS_COUNT,
  GET_LATEST_EVENTS,
  SET_EVENTS,
  SET_EVENTS_COUNT,
  SET_LATEST_EVENTS
} from "./actionTypes";

export const API_URL = getApiUrl("report");

export const getEvents = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/events`,
    method: "GET",
    onSuccess: handleSuccess(SET_EVENTS),
    label: GET_EVENTS,
    ttl: MINUTE,
    hash: hashParams({ ...params, organizationId }),
    params: {
      include_read: true,
      read_on_get: true,
      limit: 80,
      level: params.level,
      time_start: params.timeStart,
      time_end: params.timeEnd,
      last_id: params.lastId
    }
  });

export const getLatestEvents = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/events`,
    method: "GET",
    onSuccess: handleSuccess(SET_LATEST_EVENTS),
    label: GET_LATEST_EVENTS,
    params: {
      limit: 5
    }
  });

export const getEventsCount = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/events/count`,
    method: "GET",
    onSuccess: handleSuccess(SET_EVENTS_COUNT),
    hash: hashParams(organizationId),
    label: GET_EVENTS_COUNT,
    ttl: MINUTE
  });
