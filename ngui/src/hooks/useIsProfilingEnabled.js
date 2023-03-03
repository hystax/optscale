import { ORGANIZATION_FEATURE_FLAG_NAMES } from "utils/constants";
import { useIsFeatureEnabled } from "./useIsFeatureEnabled";
import { useOrganizationInfo } from "./useOrganizationInfo";

export const useIsProfilingEnabled = () => {
  const isProfilingFeatureEnabled = useIsFeatureEnabled(ORGANIZATION_FEATURE_FLAG_NAMES.ML_PROFILING_ENABLED);

  const { isDemo } = useOrganizationInfo();

  return isDemo || isProfilingFeatureEnabled;
};
