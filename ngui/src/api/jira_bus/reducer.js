import { SET_JIRA_ORGANIZATION_STATUS } from "./actionTypes";

export const JIRA_BUS = "jira_bus";

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SET_JIRA_ORGANIZATION_STATUS:
      return {
        ...state,
        [action.label]: action.payload
      };
    default:
      return state;
  }
};

export default reducer;
