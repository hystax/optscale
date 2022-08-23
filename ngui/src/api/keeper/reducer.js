import { SET_EVENTS, SET_LATEST_EVENTS } from "./actionTypes";

export const KEEPER = "keeper";

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SET_EVENTS:
      return {
        ...state,
        [action.label]: {
          events: action.payload.events
        }
      };
    case SET_LATEST_EVENTS:
      return {
        ...state,
        [action.label]: {
          events: action.payload.events
        }
      };
    // Was commented out due to the NGUI-1039 task
    // case SET_EVENTS_COUNT:
    //   return {
    //     ...state,
    //     [action.label]: {
    //       count: action.payload.count
    //     }
    //   };
    default:
      return state;
  }
};

export default reducer;
