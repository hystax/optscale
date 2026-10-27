import { Box, Stack, Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import HtmlSymbol from "components/HtmlSymbol";
import QuestionMark from "components/QuestionMark";
import { BillingSubscriptionStatus } from "graphql/__generated__/hooks/restapi";
import { useIsManageBillingSubscriptionAllowed } from "hooks/useIsManageBillingSubscriptionAllowed";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { SPACING_1, SPACING_2 } from "utils/layouts";
import { STRIPE_PLAN_NAME } from "../../../constants";
import { ManageSubscriptionButton, UpgradeToEnterpriseButton } from "../../Actions";
import Alerts from "../../Alerts";
import { type ProFeaturesProps, ProSubscriptionFeatures } from "../../Features";
import Price from "../../Price";
import StatusBadge from "../../StatusBadge";
import { BaseCard, PlanName } from "../common";

type ProSubscriptionCardProps = {
  stripePlanName: string;
  status: BillingSubscriptionStatus;
  gracePeriodStart: number;
  gracePeriodDays: number;
  endDate: number;
  cancelAtPeriodEnd: boolean;
  limits: ProFeaturesProps["limits"];
  quantity: number;
  price: number;
  currency: string;
};

const ProSubscriptionCard = ({
  stripePlanName,
  status,
  gracePeriodStart,
  gracePeriodDays,
  endDate,
  cancelAtPeriodEnd,
  limits,
  quantity,
  price,
  currency,
}: ProSubscriptionCardProps) => {
  const intl = useIntl();

  const isManageBillingSubscriptionAllowed = useIsManageBillingSubscriptionAllowed();

  const renderPrice = () => {
    if (stripePlanName === STRIPE_PLAN_NAME.PRO_MONTHLY) {
      return (
        <Price
          price={price * quantity}
          currency={currency}
          period={intl.formatMessage({ id: "month" }).toLowerCase()}
          variant="body1"
        />
      );
    }

    if (stripePlanName === STRIPE_PLAN_NAME.PRO_YEARLY) {
      return (
        <Price
          price={price * quantity}
          currency={currency}
          period={intl.formatMessage({ id: "year" }).toLowerCase()}
          variant="body1"
        />
      );
    }

    return null;
  };

  const priceElement = renderPrice();

  return (
    <BaseCard
      header={
        <Box display="flex" alignItems="center" gap={SPACING_1}>
          <Box display="flex" alignItems="center" gap={SPACING_1}>
            <span>
              <PlanName name={<FormattedMessage id="pro" />} />
              {quantity > 1 && (
                <>
                  &nbsp;
                  <Typography component="span" variant="body1">
                    (
                    <HtmlSymbol symbol="multiply" />
                    {quantity})
                  </Typography>
                </>
              )}
            </span>
            {!!priceElement && (
              <>
                {" – "}
                {priceElement}
              </>
            )}
          </Box>
          {quantity > 1 && (
            <Box display="flex" alignItems="center">
              <QuestionMark
                tooltipText={
                  <Typography>
                    <FormattedMessage
                      id="subscriptionPriceTooltip"
                      values={{
                        price: <FormattedMoney value={price} type={FORMATTED_MONEY_TYPES.COMMON} format={currency} />,
                        quantity,
                        strong: (chunks) => <strong>{chunks}</strong>,
                      }}
                    />
                  </Typography>
                }
                fontSize="small"
                color="secondary"
                withLeftMargin={false}
              />
            </Box>
          )}
          <StatusBadge status={status} />
        </Box>
      }
      body={
        <Stack spacing={SPACING_2}>
          <Alerts
            status={status}
            gracePeriodStart={gracePeriodStart}
            gracePeriodDays={gracePeriodDays}
            endDate={endDate}
            cancelAtPeriodEnd={cancelAtPeriodEnd}
          />
          <ProSubscriptionFeatures limits={limits} />
        </Stack>
      }
      footer={
        isManageBillingSubscriptionAllowed ? (
          <Box display="flex" gap={SPACING_1} flexWrap="wrap">
            <Box flex={1}>
              <ManageSubscriptionButton />
            </Box>
            <Box flex={2}>
              <UpgradeToEnterpriseButton />
            </Box>
          </Box>
        ) : null
      }
    />
  );
};

export default ProSubscriptionCard;
