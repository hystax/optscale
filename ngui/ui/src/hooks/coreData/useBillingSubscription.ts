import { useBillingSubscriptionQuery } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "../useOrganizationInfo";

export const useBillingSubscription = () => {
  const { organizationId } = useOrganizationInfo();

  const { data: { billingSubscription } = {} } = useBillingSubscriptionQuery({
    variables: {
      organizationId,
    },
    fetchPolicy: "cache-only",
  });

  return billingSubscription;
};
