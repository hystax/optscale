import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = (): FormValues => ({
  [FIELD_NAMES.NAME]: "",
  [FIELD_NAMES.DESCRIPTION]: "",
  [FIELD_NAMES.KEY]: "",
  [FIELD_NAMES.OWNER]: "",
  [FIELD_NAMES.METRICS]: []
});
