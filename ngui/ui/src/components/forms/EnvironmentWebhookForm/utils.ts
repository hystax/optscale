import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = ({ url }: { url: string }): FormValues => ({
  [FIELD_NAMES.WEBHOOK_URL]: url ?? ""
});
