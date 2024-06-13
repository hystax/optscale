import { ModelDetails } from "services/MlModelsService";
import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = (model?: ModelDetails): FormValues => ({
  [FIELD_NAMES.NAME]: model?.name ?? "",
  [FIELD_NAMES.KEY]: model?.key ?? "",
  [FIELD_NAMES.DESCRIPTION]: model?.description ?? "",
  [FIELD_NAMES.TAGS_FIELD_ARRAY.FIELD_NAME]: model?.tags
    ? Object.entries(model.tags).map(([key, value]) => ({
        [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY]: key,
        [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE]: value
      }))
    : [
        {
          [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY]: "",
          [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE]: ""
        }
      ]
});
