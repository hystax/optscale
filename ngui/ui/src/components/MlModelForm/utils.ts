import { ModelDetails } from "services/MlModelsService";
import { FIELD_NAMES } from "./FormElements";
import { FormValues } from "./types";

export const getDefaultValues = (model?: ModelDetails): FormValues => ({
  [FIELD_NAMES.NAME_FIELD_NAME]: model?.name ?? "",
  [FIELD_NAMES.KEY_FIELD_NAME]: model?.key ?? "",
  [FIELD_NAMES.DESCRIPTION_FIELD_NAME]: model?.description ?? "",
  [FIELD_NAMES.TAGS_FIELD_ARRAY.FIELD_NAME]: model?.tags
    ? Object.entries(model.tags).map(([key, value]) => ({
        [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY_FIELD_NAME]: key,
        [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE_FIELD_NAME]: value
      }))
    : [
        {
          [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY_FIELD_NAME]: "",
          [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE_FIELD_NAME]: ""
        }
      ]
});
