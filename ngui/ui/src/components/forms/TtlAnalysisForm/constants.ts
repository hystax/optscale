import { TTL_MODES } from "utils/constants";

export const FIELD_NAMES = Object.freeze({
  POOL_ID: "poolId",
  TTL_MODE: "ttlMode",
  CUSTOM_TTL: TTL_MODES.CUSTOM_TTL,
  PREDEFINED_TTL: TTL_MODES.PREDEFINED_TTL,
  START_DATE_PICKER_NAME: "startDate",
  END_DATE_PICKER_NAME: "endDate"
});
