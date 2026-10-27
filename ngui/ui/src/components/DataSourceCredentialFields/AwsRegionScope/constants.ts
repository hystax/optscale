import { RUNSET_TEMPLATE_REGIONS } from "utils/constants";

export const FIELD_NAMES = Object.freeze({
  MODE: "regionScopeMode",
  INCLUDED_REGIONS: "regionScopeIncludedRegions",
  EXCLUDED_REGIONS: "regionScopeExcludedRegions",
});

export const REGION_SCOPE_MODES = Object.freeze({
  ALL: "all",
  INCLUDE: "include",
  EXCLUDE: "exclude",
});

export const AWS_REGION_CODES = RUNSET_TEMPLATE_REGIONS.map(({ id }) => id);
