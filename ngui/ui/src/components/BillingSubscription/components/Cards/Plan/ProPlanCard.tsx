import { useState } from "react";
import { Box, Stack, Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import ButtonGroup from "components/ButtonGroup";
import { SPACING_1, SPACING_2 } from "utils/layouts";
import { ObjectValues } from "utils/types";
import { BILLING_CYCLE } from "../../../constants";
import { UpgradeSubscriptionButton } from "../../Actions";
import { ProPlanFeatures } from "../../Features";
import Price from "../../Price";
import { BaseCard, PlanName } from "../common";

export type BillingCycle = ObjectValues<typeof BILLING_CYCLE>;

type ProPlanCardProps = {
  monthlyPlan: {
    id: string;
    price: number;
    currency: string;
  };
  annualPlan: {
    id: string;
    price: number;
    currency: string;
  };
};

const ProPlanCard = ({ monthlyPlan, annualPlan }: ProPlanCardProps) => {
  const intl = useIntl();

  const [billingCycle, setBillingCycle] = useState<BillingCycle>(BILLING_CYCLE.MONTHLY);

  const buttonsGroupDefinition = [
    {
      id: BILLING_CYCLE.MONTHLY,
      messageId: "subscriptionBillingCycle.monthly",
      action: () => setBillingCycle(BILLING_CYCLE.MONTHLY),
    },
    {
      id: BILLING_CYCLE.ANNUAL,
      messageId: "subscriptionBillingCycle.annual",
      action: () => setBillingCycle(BILLING_CYCLE.ANNUAL),
    },
  ];

  const { id, monthlyPrice, annualPrice, currency } =
    billingCycle === BILLING_CYCLE.MONTHLY
      ? {
          id: monthlyPlan.id,
          monthlyPrice: monthlyPlan.price,
          annualPrice: monthlyPlan.price * 12,
          currency: monthlyPlan.currency,
        }
      : {
          id: annualPlan.id,
          monthlyPrice: annualPlan.price / 12,
          annualPrice: annualPlan.price,
          currency: annualPlan.currency,
        };

  return (
    <BaseCard
      header={
        <Box display="flex" gap={SPACING_1} alignItems="center" justifyContent="space-between" flexGrow={1} flexWrap="wrap">
          <Box display="flex" gap={SPACING_1} alignItems="center" flexWrap="wrap">
            <PlanName name={<FormattedMessage id="pro" />} />
            {" – "}
            <Price
              price={monthlyPrice}
              currency={currency}
              unit={intl.formatMessage({ id: "dataSource" }).toLowerCase()}
              period={intl.formatMessage({ id: "month" }).toLowerCase()}
              variant="body1"
            />
            {" – "}
            <Price
              price={annualPrice}
              currency={currency}
              period={intl.formatMessage({ id: "year" }).toLowerCase()}
              variant="body1"
            />
          </Box>
          <Box>
            <ButtonGroup buttons={buttonsGroupDefinition} activeButtonId={billingCycle} />
          </Box>
        </Box>
      }
      body={
        <Stack spacing={SPACING_2}>
          <Typography variant="body2" fontWeight="bold">
            <FormattedMessage id="everythingInFreePlus" />
          </Typography>
          <ProPlanFeatures />
        </Stack>
      }
      footer={
        <UpgradeSubscriptionButton
          text={`${intl.formatMessage({ id: "get" })} ${intl.formatMessage({ id: "pro" })}`}
          billingSubscriptionPlanId={id}
        />
      }
    />
  );
};

export default ProPlanCard;
