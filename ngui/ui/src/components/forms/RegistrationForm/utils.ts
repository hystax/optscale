import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = ({ email }: { email?: string }): FormValues => ({
  [FIELD_NAMES.EMAIL]: email ?? "",
  [FIELD_NAMES.FULL_NAME]: "",
  [FIELD_NAMES.PASSWORD]: "",
  [FIELD_NAMES.CONFIRM_PASSWORD]: ""
});
