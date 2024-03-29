import { isEmpty as isEmptyObject } from "utils/objects";
import { FIELD_NAMES } from "./FormElements";
import { FormValues, Tags } from "./types";

export const getDefaultValues = (tags: Tags): FormValues => ({
  [FIELD_NAMES.TAGS_FIELD_ARRAY.FIELD_NAME]: isEmptyObject(tags)
    ? [
        {
          [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY_FIELD_NAME]: "",
          [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE_FIELD_NAME]: ""
        }
      ]
    : Object.entries(tags).map(([key, value]) => ({
        [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY_FIELD_NAME]: key,
        [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE_FIELD_NAME]: value
      }))
});
