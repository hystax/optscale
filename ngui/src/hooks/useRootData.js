import { createSelector } from "reselect";
import { useShallowEqualSelector } from "hooks/useShallowEqualSelector";

const filter = (state, label, callback) => (typeof callback === "function" ? callback(state[label]) : state[label]);

const selector = createSelector(filter, (result) => result);

export const useRootData = (label, callback) => ({
  rootData: useShallowEqualSelector((state) => selector(state, label, callback))
});
