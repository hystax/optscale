import { FormattedMessage } from "react-intl";
import FeaturesList from "../FeaturesList";

const features = [
  "billingSubscriptionFeatures.unlimitedMonthlyExpenses",
  "billingSubscriptionFeatures.unlimitedDataSources",
  "billingSubscriptionFeatures.privateDeployment",
  "billingSubscriptionFeatures.accessToRoadmap",
  "billingSubscriptionFeatures.prioritizedPoolRequestReview",
  "billingSubscriptionFeatures.dedicated24HourSupportSevenDaysAWeek",
] as const;

const EnterpriseSubscriptionFeatures = () => (
  <FeaturesList>
    {features.map((feature) => (
      <li key={feature}>
        <FormattedMessage id={feature} />
      </li>
    ))}
  </FeaturesList>
);

export default EnterpriseSubscriptionFeatures;
