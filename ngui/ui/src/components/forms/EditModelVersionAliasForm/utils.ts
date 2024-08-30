import { ModelVersion } from "services/MlModelsService";
import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = (modelVersion: ModelVersion): FormValues => ({
  [FIELD_NAMES.ALIASES]: modelVersion?.aliases ?? []
});
