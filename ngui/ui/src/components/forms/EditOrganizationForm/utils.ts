import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = ({ organizationName }: { organizationName: string }): FormValues => ({
  [FIELD_NAMES.ORGANIZATION_NAME]: organizationName
});
