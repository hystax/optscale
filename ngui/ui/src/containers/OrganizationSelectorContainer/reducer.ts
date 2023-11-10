import { SET_SCOPE_ID } from "./actionTypes";

export const SCOPE_ID = "organizationId";

export const INITIAL_SCOPE_ID = "";

const reducer = (state = INITIAL_SCOPE_ID, action) => {
  switch (action.type) {
    case SET_SCOPE_ID: {
      return action.organizationId;
    }
    default:
      return state;
  }
};

export default reducer;
