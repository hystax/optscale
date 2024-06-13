import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = (): FormValues => ({
  [FIELD_NAMES.NEW_DEFAULT_SSH_KEY]: ""
});
