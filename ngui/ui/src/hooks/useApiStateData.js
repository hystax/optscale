import { createSelector } from "reselect";
import { API } from "api/reducer";
import { useShallowEqualSelector } from "hooks/useShallowEqualSelector";

const apiSelector = (state) => state[API];

const apiStateSelector = createSelector(
  apiSelector,
  (_, label) => label,
  (api, label) => api[label] || {}
);

export const useApiStateData = (label) => ({
  apiStateData: useShallowEqualSelector((state) => apiStateSelector(state, label))
});
