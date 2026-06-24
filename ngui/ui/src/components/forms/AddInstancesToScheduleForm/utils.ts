import { FIELD_NAMES } from "./constants";

export const getDefaultValue = () => ({
  [FIELD_NAMES.DATA_SOURCES]: [],
  [FIELD_NAMES.INSTANCES]: {},
  [FIELD_NAMES.FILTERS]: {},
  [FIELD_NAMES.TAG_INCLUDE_EC2]: true,
  [FIELD_NAMES.TAG_INCLUDE_RDS]: true,
  [FIELD_NAMES.TAG_ENTRIES]: [{ key: "", value: "" }],
});
