import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = ({
  propertyName,
  propertyValue
}: {
  propertyName: string;
  propertyValue: string;
}): FormValues => ({
  [FIELD_NAMES.PROPERTY_NAME]: propertyName,
  [FIELD_NAMES.PROPERTY_VALUE]: propertyValue
});
