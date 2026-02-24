import { FormattedMessage } from "react-intl";
import FeaturesList from "../FeaturesList";

const featureMessageIds = [
  "billingSubscriptionFeatures.privateDeployment",
  "billingSubscriptionFeatures.prioritizedPoolRequestReview",
  "billingSubscriptionFeatures.accessToRoadmap",
  "billingSubscriptionFeatures.dedicated24HourSupportSevenDaysAWeek",
] as const;

const EnterprisePlanFeatures = () => (
  <FeaturesList>
    {featureMessageIds.map((featureMessageId) => (
      <li key={featureMessageId}>
        <FormattedMessage id={featureMessageId} />
      </li>
    ))}
  </FeaturesList>
);

export default EnterprisePlanFeatures;
