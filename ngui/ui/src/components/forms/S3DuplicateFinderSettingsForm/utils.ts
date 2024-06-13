import { FIELD_NAMES } from "./constants";
import { DefaultValuesParams, FormValues } from "./types";

export const getDefaultValues = ({ requiringAttention, critical }: DefaultValuesParams = {}): FormValues => ({
  [FIELD_NAMES.REQUIRING_ATTENTION]: requiringAttention ? requiringAttention.toString() : "",
  [FIELD_NAMES.CRITICAL]: critical ? critical.toString() : ""
});
