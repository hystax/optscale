import { FIELD_NAMES } from "./constants";

export const getDefaultValue = () => ({
  [FIELD_NAMES.DATA_SOURCES]: [],
  [FIELD_NAMES.INSTANCES]: {},
  [FIELD_NAMES.FILTERS]: {}
});
