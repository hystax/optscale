import { BillingSubscription, OrganizationSummary } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { STRIPE_PLAN_NAME } from "../../../constants";
import EnterpriseSubscriptionCard from "./EnterpriseSubscriptionCard";
import FreeSubscriptionCard from "./FreeSubscriptionCard";
import ProSubscriptionCard from "./ProSubscriptionCard";

type SubscriptionCardProps = {
  billingSubscription: BillingSubscription;
  organizationSummary: OrganizationSummary;
};

const SubscriptionCard = ({ billingSubscription, organizationSummary }: SubscriptionCardProps) => {
  const { organizationId } = useOrganizationInfo();

  const {
    plan,
    quantity,
    status,
    grace_period_start: gracePeriodStart,
    end_date: endDate,
    cancel_at_period_end: cancelAtPeriodEnd,
  } = billingSubscription;

  const {
    name,
    price,
    limits,
    grace_period_days: gracePeriodDays,
    currency,
    qty_unit: quantityUnit,
    customer_id: customerId,
  } = plan;

  if (organizationId === customerId) {
    return (
      <EnterpriseSubscriptionCard
        status={status}
        gracePeriodStart={gracePeriodStart}
        gracePeriodDays={gracePeriodDays}
        endDate={endDate}
        cancelAtPeriodEnd={cancelAtPeriodEnd}
      />
    );
  }

  const getLimit = (limitName: "cloud_accounts") => ({
    current: organizationSummary?.entities?.[limitName] ?? 0,
    limit: (limits?.[limitName] ?? 1) as number,
    quantity: quantityUnit === limitName ? quantity : 1,
  });

  if (name === STRIPE_PLAN_NAME.PRO_MONTHLY || name === STRIPE_PLAN_NAME.PRO_YEARLY) {
    return (
      <ProSubscriptionCard
        stripePlanName={name}
        status={status}
        gracePeriodStart={gracePeriodStart}
        gracePeriodDays={gracePeriodDays}
        endDate={endDate}
        cancelAtPeriodEnd={cancelAtPeriodEnd}
        limits={{
          dataSources: getLimit("cloud_accounts"),
        }}
        quantity={quantity}
        price={price!}
        currency={currency!}
      />
    );
  }

  if (name === STRIPE_PLAN_NAME.FREE) {
    return (
      <FreeSubscriptionCard
        status={status}
        // @ts-expect-error: The correct type should come from Apollo
        monthExpenses={organizationSummary?.entities?.month_expenses ?? {}}
        // @ts-expect-error: The correct type should come from Apollo
        monthlyExpensesLimit={limits?.month_expenses ?? 0}
        gracePeriodStart={gracePeriodStart}
        gracePeriodDays={gracePeriodDays}
        endDate={endDate}
        cancelAtPeriodEnd={cancelAtPeriodEnd}
      />
    );
  }

  return null;
};

export default SubscriptionCard;
