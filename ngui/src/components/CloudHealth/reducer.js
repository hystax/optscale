import { AWS_CNR, AZURE_CNR } from "utils/constants";
import { TOGGLE_DOMESTIC_REGIONS_SWITCH, TOGGLE_CLOUD_TYPE_CHECKBOXES } from "./actionTypes";

export const CLOUD_HEALTH = "cloudHealth";

const initialState = {
  domesticRegionsSwitchState: false,
  cloudTypeCheckboxesState: { [AWS_CNR]: true, [AZURE_CNR]: true }
};

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case TOGGLE_DOMESTIC_REGIONS_SWITCH: {
      return { ...state, domesticRegionsSwitchState: !state.domesticRegionsSwitchState };
    }
    case TOGGLE_CLOUD_TYPE_CHECKBOXES: {
      return {
        ...state,
        cloudTypeCheckboxesState: {
          ...state.cloudTypeCheckboxesState,
          [action.payload]: !state.cloudTypeCheckboxesState[action.payload]
        }
      };
    }
    default:
      return state;
  }
};

export default reducer;
