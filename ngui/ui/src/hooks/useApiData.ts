import { createSelector } from "reselect";
import { RESTAPI, AUTH, JIRA_BUS } from "api";
import { useShallowEqualSelector } from "hooks/useShallowEqualSelector";

const restApiSelector = (state) => state[RESTAPI];
const authSelector = (state) => state[AUTH];
const jiraBusSelector = (state) => state[JIRA_BUS];

const apiSelector = createSelector(
  restApiSelector,
  authSelector,
  jiraBusSelector,
  (_, props) => props,
  (...args) => {
    const [restapi, auth, jiraBus, { label, defaultValue }] = args;
    return { ...restapi, ...auth, ...jiraBus }[label] || defaultValue;
  }
);

export const useApiData = (label, defaultValue = {}) => ({
  apiData: useShallowEqualSelector((state) => apiSelector(state, { label, defaultValue }))
});
