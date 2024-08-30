import { FIELD_NAMES } from "./constants";
import { FormValues } from "./type";

export const getDefaultValues = ({ cost }: { cost: number }): FormValues => ({
  [FIELD_NAMES.COST]: String(cost)
});
