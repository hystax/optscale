import { START_TOUR, FINISH_TOUR } from "./actionTypes";

export const TOURS = "tours";
export const PRODUCT_TOUR = "productTour";
export const ENVIRONMENTS_TOUR = "environmentsTour";

const INITIAL_STATE = {
  [PRODUCT_TOUR]: {
    isOpen: false,
    isFinished: false
  },
  [ENVIRONMENTS_TOUR]: {
    isOpen: false,
    isFinished: false
  }
};

const reducer = (state = INITIAL_STATE, action) => {
  switch (action.type) {
    case START_TOUR: {
      return {
        ...state,
        [action.label]: {
          isOpen: true,
          isFinished: false
        }
      };
    }
    case FINISH_TOUR: {
      return {
        ...state,
        [action.label]: {
          isOpen: false,
          isFinished: true
        }
      };
    }
    default:
      return state;
  }
};

export default reducer;
