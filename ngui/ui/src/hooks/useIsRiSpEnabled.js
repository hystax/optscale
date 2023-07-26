import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useIsFeatureEnabled } from "./useIsFeatureEnabled";

export const useIsRiSpEnabled = () => {
  const isFeatureEnabled = useIsFeatureEnabled("ri_sp_enabled");
  const { isDemo } = useOrganizationInfo();

  return isFeatureEnabled || isDemo;
};
