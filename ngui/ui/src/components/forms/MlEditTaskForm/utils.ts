import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = (task = {}): FormValues => ({
  [FIELD_NAMES.NAME]: task?.name ?? "",
  [FIELD_NAMES.DESCRIPTION]: task?.description ?? "",
  [FIELD_NAMES.OWNER]: task?.owner_id ?? ""
});
