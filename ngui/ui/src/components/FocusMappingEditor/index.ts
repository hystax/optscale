import { FOCUS_MAPPING_FIELD_NAME, MAPPING_FIELDS } from "./constants";
import FocusMappingEditor from "./FocusMappingEditor";
import { getDefaultFocusMappingFormValues, isEmptyApiMapping, mappingApiToFormValues, mappingFormValuesToApi } from "./mapping";

export type { ApiMapping, FocusMappingFormValues } from "./types";

export {
  FOCUS_MAPPING_FIELD_NAME,
  MAPPING_FIELDS,
  getDefaultFocusMappingFormValues,
  isEmptyApiMapping,
  mappingApiToFormValues,
  mappingFormValuesToApi,
};

export default FocusMappingEditor;
