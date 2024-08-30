import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = ({ hourlyPrice }: { hourlyPrice?: number }): FormValues => ({
  [FIELD_NAMES.HOURLY_PRICE]: hourlyPrice ?? 0
});
