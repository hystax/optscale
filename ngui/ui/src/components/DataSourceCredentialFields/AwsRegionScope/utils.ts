import { isEmptyArray } from "utils/arrays";
import { FIELD_NAMES, REGION_SCOPE_MODES } from "./constants";
import { AwsRegionScopeConfig } from "./types";

export const getRegionScopeDefaultValues = (config: AwsRegionScopeConfig = {}) => {
  if (!isEmptyArray(config.included_regions)) {
    return {
      [FIELD_NAMES.MODE]: REGION_SCOPE_MODES.INCLUDE,
      [FIELD_NAMES.INCLUDED_REGIONS]: config.included_regions,
      [FIELD_NAMES.EXCLUDED_REGIONS]: [],
    };
  }

  if (!isEmptyArray(config.excluded_regions)) {
    return {
      [FIELD_NAMES.MODE]: REGION_SCOPE_MODES.EXCLUDE,
      [FIELD_NAMES.INCLUDED_REGIONS]: [],
      [FIELD_NAMES.EXCLUDED_REGIONS]: config.excluded_regions,
    };
  }

  return {
    [FIELD_NAMES.MODE]: REGION_SCOPE_MODES.ALL,
    [FIELD_NAMES.INCLUDED_REGIONS]: [],
    [FIELD_NAMES.EXCLUDED_REGIONS]: [],
  };
};

export const getRegionScopeConfigParams = (formData: Record<string, unknown>) => {
  const mode = formData[FIELD_NAMES.MODE];

  if (mode === REGION_SCOPE_MODES.INCLUDE) {
    return { included_regions: formData[FIELD_NAMES.INCLUDED_REGIONS] as string[] };
  }

  if (mode === REGION_SCOPE_MODES.EXCLUDE) {
    return { excluded_regions: formData[FIELD_NAMES.EXCLUDED_REGIONS] as string[] };
  }

  return {};
};
