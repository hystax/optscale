import { ModelVersion } from "services/MlModelsService";
import { FIELD_NAMES } from "./constants";

export const getDefaultValues = (modelVersion: ModelVersion) => ({
  [FIELD_NAMES.PATH]: modelVersion?.path ?? ""
});
