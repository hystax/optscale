import { createSelector } from "reselect";
import { RESTAPI, AUTH, KEEPER, SLACKER, JIRA_BUS } from "api";
import { useShallowEqualSelector } from "hooks/useShallowEqualSelector";

const restApiSelector = (state) => state[RESTAPI];
const authSelector = (state) => state[AUTH];
const keeperSelector = (state) => state[KEEPER];
const slackerSelector = (state) => state[SLACKER];
const jiraBusSelector = (state) => state[JIRA_BUS];

const apiSelector = createSelector(
  restApiSelector,
  authSelector,
  keeperSelector,
  slackerSelector,
  jiraBusSelector,
  (_, props) => props,
  (...args) => {
    const [restapi, auth, keeper, slacker, jiraBus, { label, defaultValue }] = args;
    return { ...restapi, ...auth, ...keeper, ...slacker, ...jiraBus }[label] || defaultValue;
  }
);

export const useApiData = (label, defaultValue = {}) => ({
  apiData: useShallowEqualSelector((state) => apiSelector(state, { label, defaultValue }))
});
