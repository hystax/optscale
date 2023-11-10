import { CHANGE_SORT_GROUPS_BY } from "./actionTypes";
import { SORT_GROUPS_BY } from "./SortGroupsBySelector";

export const RESOURCES_SORT_GROUPS_BY = "resourcesSortGroupsBy";

const reducer = (state = SORT_GROUPS_BY[0].value, action) => {
  switch (action.type) {
    case CHANGE_SORT_GROUPS_BY:
      return action.value;
    default:
      return state;
  }
};

export default reducer;
