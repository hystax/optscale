import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = (): FormValues => ({
  [FIELD_NAMES.DATA_SOURCES]: [],
  [FIELD_NAMES.BUCKETS]: {},
  [FIELD_NAMES.SIZE]: "0"
});
