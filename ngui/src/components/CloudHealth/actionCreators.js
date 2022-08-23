import { TOGGLE_DOMESTIC_REGIONS_SWITCH, TOGGLE_CLOUD_TYPE_CHECKBOXES } from "./actionTypes";

export const toggleDomesticRegionsSwitch = () => ({
  type: TOGGLE_DOMESTIC_REGIONS_SWITCH
});

export const toggleCloudTypeCheckboxes = (cloudType) => ({
  type: TOGGLE_CLOUD_TYPE_CHECKBOXES,
  payload: cloudType
});
