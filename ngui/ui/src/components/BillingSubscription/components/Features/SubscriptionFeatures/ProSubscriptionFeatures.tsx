import { FormattedMessage, useIntl } from "react-intl";
import LimitLabel from "../../LimitLabel";
import FeaturesList from "../FeaturesList";

export type ProFeaturesProps = {
  limits: {
    dataSources: {
      current: number;
      limit: number;
      quantity: number;
    };
  };
};

const features = [
  "billingSubscriptionFeatures.unlimitedMonthlyExpenses",
  "billingSubscriptionFeatures.24HourSupportSevenDaysAWeek",
] as const;

const ProSubscriptionFeatures = ({ limits }: ProFeaturesProps) => {
  const intl = useIntl();

  return (
    <FeaturesList>
      <li>
        <LimitLabel
          value={limits.dataSources.current}
          limit={limits.dataSources.limit}
          quantity={limits.dataSources.quantity}
          entityName={intl.formatMessage({ id: "billingSubscriptionFeatures.dataSources" })}
        />
      </li>
      {features.map((feature) => (
        <li key={feature}>
          <FormattedMessage id={feature} />
        </li>
      ))}
    </FeaturesList>
  );
};

export default ProSubscriptionFeatures;
