import { useMemo } from "react";
import { useIntl } from "react-intl";
import { useOrganizationInfo } from "./useOrganizationInfo";

const useDemoOrganizationRestrictions = () => {
  const intl = useIntl();
  const { isDemo } = useOrganizationInfo();

  return {
    isRestricted: isDemo,
    restrictionReasonMessage: intl.formatMessage({ id: "notAvailableInLiveDemo" }),
  };
};

const useInactiveOrganizationRestrictions = () => {
  const intl = useIntl();
  const { isInactive } = useOrganizationInfo();

  return {
    isRestricted: isInactive,
    restrictionReasonMessage: intl.formatMessage({ id: "notAvailableForInactiveOrganization" }),
  };
};

export const useOrganizationActionRestrictions = () => {
  const demoRestrictions = useDemoOrganizationRestrictions();
  const inactiveRestrictions = useInactiveOrganizationRestrictions();

  const restrictionReasonMessage = useMemo(() => {
    if (demoRestrictions.isRestricted) {
      return demoRestrictions.restrictionReasonMessage;
    }
    if (inactiveRestrictions.isRestricted) {
      return inactiveRestrictions.restrictionReasonMessage;
    }
    return undefined;
  }, [
    demoRestrictions.isRestricted,
    demoRestrictions.restrictionReasonMessage,
    inactiveRestrictions.isRestricted,
    inactiveRestrictions.restrictionReasonMessage,
  ]);

  return {
    isRestricted: demoRestrictions.isRestricted || inactiveRestrictions.isRestricted,
    restrictionReasonMessage,
  };
};
