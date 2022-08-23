export const ALL_CATEGORY = "all";
export const COST_CATEGORY = "cost";
export const PERFORMANCE_CATEGORY = "performance";
export const SECURITY_CATEGORY = "security";

export const CATEGORIES = Object.freeze({
  [ALL_CATEGORY]: "all",
  [COST_CATEGORY]: "costOptimization",
  [SECURITY_CATEGORY]: "security"
});

export const SUPPORTED_CATEGORIES = Object.freeze(Object.keys(CATEGORIES));
