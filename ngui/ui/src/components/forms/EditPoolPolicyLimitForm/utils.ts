import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = (policyLimit?: number): FormValues => ({
  [FIELD_NAMES.LIMIT]: policyLimit ? String(policyLimit) : ""
});
