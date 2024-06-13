import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = ({ name }: { name: string }): FormValues => ({
  [FIELD_NAMES.NAME]: name
});
