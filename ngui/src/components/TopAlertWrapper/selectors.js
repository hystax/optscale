import { useShallowEqualSelector } from "hooks/useShallowEqualSelector";
import { ALERTS } from "./reducer";

export const useAllAlertsSelector = (organizationId) => {
  const allAlerts = useShallowEqualSelector((state) => {
    const alerts = state[ALERTS];

    const currentOrganizationAlerts = alerts[organizationId] || [];

    return currentOrganizationAlerts;
  });
  return allAlerts;
};
