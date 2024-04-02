import { MlCreateModelFormButtons as CreateFormButtons, MlEditModelFormButtons as EditFormButtons } from "./MlModelFormButtons";
import DescriptionField, { FIELD_NAME as DESCRIPTION_FIELD_NAME } from "./MlModelFormDescriptionField";
import KeyField, { FIELD_NAME as KEY_FIELD_NAME } from "./MlModelFormKeyField";
import NameField, { FIELD_NAME as NAME_FIELD_NAME } from "./MlModelFormNameField";
import TagsFieldArray, {
  ARRAY_FIELD_NAME as TAGS_ARRAY_FIELD_NAME,
  KEY_FIELD_NAME as TAG_KEY_FIELD_NAME,
  VALUE_FIELD_NAME as TAG_VALUE_FIELD_NAME
} from "./MlModelFormTagsFieldArray";

const FIELD_NAMES = Object.freeze({
  NAME_FIELD_NAME,
  KEY_FIELD_NAME,
  DESCRIPTION_FIELD_NAME,
  TAGS_FIELD_ARRAY: Object.freeze({
    FIELD_NAME: TAGS_ARRAY_FIELD_NAME,
    KEY_FIELD_NAME: TAG_KEY_FIELD_NAME,
    VALUE_FIELD_NAME: TAG_VALUE_FIELD_NAME
  })
});

export { NameField, KeyField, DescriptionField, TagsFieldArray, CreateFormButtons, EditFormButtons, FIELD_NAMES };
