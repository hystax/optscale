import { FormattedMessage } from "react-intl";
import { BillingSubscriptionStatus } from "graphql/__generated__/hooks/restapi";
import { EnterpriseSubscriptionFeatures } from "../../Features";
import { BaseCard, PlanName, SubscriptionCardBody, SubscriptionCardHeader } from "../common";

type EnterpriseSubscriptionCardProps = {
  status: BillingSubscriptionStatus;
  gracePeriodStart: number;
  gracePeriodDays: number;
  endDate: number;
  cancelAtPeriodEnd: boolean;
};

const EnterpriseSubscriptionCard = ({
  status,
  gracePeriodStart,
  gracePeriodDays,
  endDate,
  cancelAtPeriodEnd,
}: EnterpriseSubscriptionCardProps) => (
  <BaseCard
    header={<SubscriptionCardHeader content={<PlanName name={<FormattedMessage id="enterprise" />} />} status={status} />}
    body={
      <SubscriptionCardBody
        features={<EnterpriseSubscriptionFeatures />}
        status={status}
        gracePeriodStart={gracePeriodStart}
        gracePeriodDays={gracePeriodDays}
        endDate={endDate}
        cancelAtPeriodEnd={cancelAtPeriodEnd}
      />
    }
  />
);

export default EnterpriseSubscriptionCard;
