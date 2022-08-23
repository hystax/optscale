import { RANGE_DATES } from "containers/RangePickerFormContainer/reducer";
import { millisecondsToSeconds } from "utils/datetime";
import { objectMap } from "utils/objects";

export const CURRENT_VERSION = 7;

// When we modify storage structure, we will need to properly use migrations:
// https://github.com/rt2zz/redux-persist/blob/master/docs/migrations.md
const migrations = {
  2: (state) => {
    // migration of saved date ranges from ms to s
    const secondsRanges = objectMap(state[RANGE_DATES], (range) => objectMap(range, (value) => millisecondsToSeconds(value)));
    return {
      ...state,
      [RANGE_DATES]: secondsRanges
    };
  },
  3: (state) => {
    // deleting an obsolete key related to menu items
    const { mainMenuItems: _, ...rest } = state;
    return rest;
  },
  4: (state) => {
    // moving the old key to the new structure
    const { productTour, ...rest } = state;
    return {
      ...rest,
      tours: {
        ...state.tours,
        productTour: {
          ...productTour
        }
      }
    };
  },
  5: (state) => {
    // top alerts now have different ids, so we saving each one
    const singleIdState = state.topAlertClose;
    const closedAlertsIds = singleIdState ? [{ id: singleIdState, closed: true }] : [];
    return {
      ...state,
      topAlertClose: closedAlertsIds
    };
  },
  6: (state) => {
    // unmark closed green alert
    const patchedData = state.topAlertClose.map((element) =>
      element.id === 3 ? { id: 3, closed: false, triggered: false } : element
    );
    return {
      ...state,
      topAlertClose: patchedData
    };
  },
  7: (state) => {
    const { topAlertClose, ...restState } = state;
    return {
      ...restState,
      alerts: {}
    };
  }
};

export default migrations;
