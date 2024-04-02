import Buttons from "./EditModelVersionTagsFormButtons";
import TagsFieldArray, {
  ARRAY_FIELD_NAME as TAGS_ARRAY_FIELD_NAME,
  KEY_FIELD_NAME as TAG_KEY_FIELD_NAME,
  VALUE_FIELD_NAME as TAG_VALUE_FIELD_NAME
} from "./EditModelVersionTagsTagsFieldArray";

const FIELD_NAMES = Object.freeze({
  TAGS_FIELD_ARRAY: Object.freeze({
    FIELD_NAME: TAGS_ARRAY_FIELD_NAME,
    KEY_FIELD_NAME: TAG_KEY_FIELD_NAME,
    VALUE_FIELD_NAME: TAG_VALUE_FIELD_NAME
  })
});

export { TagsFieldArray, Buttons, FIELD_NAMES };
