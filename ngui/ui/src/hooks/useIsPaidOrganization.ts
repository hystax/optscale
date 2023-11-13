import { useIsFeatureEnabled } from "./useIsFeatureEnabled";

export const useIsPaidOrganization = () => useIsFeatureEnabled("paid_organization");
