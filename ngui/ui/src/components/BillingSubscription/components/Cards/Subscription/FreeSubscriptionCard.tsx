import { FormattedMessage } from "react-intl";
import { BillingSubscriptionStatus } from "graphql/__generated__/hooks/restapi";
import { FreeFeaturesProps, FreeSubscriptionFeatures } from "../../Features";
import { BaseCard, PlanName, SubscriptionCardBody, SubscriptionCardHeader } from "../common";

type FreeSubscriptionCardProps = {
  status: BillingSubscriptionStatus;
  monthExpenses: FreeFeaturesProps["monthExpenses"];
  monthlyExpensesLimit: FreeFeaturesProps["monthlyExpensesLimit"];
  gracePeriodStart: number;
  gracePeriodDays: number;
  endDate: number;
  cancelAtPeriodEnd: boolean;
};

const FreeSubscriptionCard = ({
  status,
  monthExpenses,
  monthlyExpensesLimit,
  gracePeriodStart,
  gracePeriodDays,
  endDate,
  cancelAtPeriodEnd,
}: FreeSubscriptionCardProps) => (
  <BaseCard
    header={<SubscriptionCardHeader content={<PlanName name={<FormattedMessage id="free" />} />} status={status} />}
    body={
      <SubscriptionCardBody
        features={<FreeSubscriptionFeatures monthExpenses={monthExpenses} monthlyExpensesLimit={monthlyExpensesLimit} />}
        status={status}
        gracePeriodStart={gracePeriodStart}
        gracePeriodDays={gracePeriodDays}
        endDate={endDate}
        cancelAtPeriodEnd={cancelAtPeriodEnd}
      />
    }
  />
);

export default FreeSubscriptionCard;
