import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = (): FormValues => ({
  [FIELD_NAMES.EMAIL]: "",
  [FIELD_NAMES.SUBSCRIBE_TO_NEWSLETTER]: true
});
