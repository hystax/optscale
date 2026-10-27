import { FormattedMessage } from "react-intl";
import FeaturesList from "../FeaturesList";

const featureMessageIds = [
  "billingSubscriptionFeatures.unlimitedMonthlyExpenses",
  "billingSubscriptionFeatures.24HourSupportSevenDaysAWeek",
] as const;

const ProPlanFeatures = () => (
  <FeaturesList>
    {featureMessageIds.map((featureMessageId) => (
      <li key={featureMessageId}>
        <FormattedMessage id={featureMessageId} />
      </li>
    ))}
  </FeaturesList>
);

export default ProPlanFeatures;
