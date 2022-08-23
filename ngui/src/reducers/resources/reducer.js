import { OWNED, MANAGED, REQUESTED } from "utils/constants";
import { SET_POOL_ID, SET_OWNER_ID, SET_EMPLOYEE_ID, SET_ACTIVE_TAB, RESET_RESOURCES } from "./actionTypes";

export const RESOURCES = "resources";

const initialState = {
  [OWNED]: { tabIndex: 0, poolId: "", ownerId: "", employeeId: "" },
  [MANAGED]: { tabIndex: 0, poolId: "", ownerId: "", employeeId: "" },
  [REQUESTED]: { poolId: "" }
};

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case SET_ACTIVE_TAB:
      return { ...state, [action.splitGroup]: { ...state[action.splitGroup], tabIndex: action.tabIndex } };
    case SET_POOL_ID:
      return { ...state, [action.splitGroup]: { ...state[action.splitGroup], poolId: action.poolId } };
    case SET_OWNER_ID:
      return { ...state, [action.splitGroup]: { ...state[action.splitGroup], ownerId: action.ownerId } };
    case SET_EMPLOYEE_ID:
      return { ...state, [action.splitGroup]: { ...state[action.splitGroup], employeeId: action.employeeId } };
    case RESET_RESOURCES:
      return initialState;
    default:
      return state;
  }
};

export default reducer;
