import { isEmpty as isEmptyObject } from "utils/objects";
import { FIELD_NAMES } from "./constants";
import { FormValues, Tags } from "./types";

export const getDefaultValues = (tags: Tags): FormValues => ({
  [FIELD_NAMES.TAGS_FIELD_ARRAY.FIELD_NAME]: isEmptyObject(tags)
    ? [
        {
          [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY]: "",
          [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE]: ""
        }
      ]
    : Object.entries(tags).map(([key, value]) => ({
        [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY]: key,
        [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE]: value
      }))
});
