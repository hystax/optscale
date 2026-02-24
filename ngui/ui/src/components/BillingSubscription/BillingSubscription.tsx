import { Box, Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import SomethingWentWrong from "components/SomethingWentWrong";
import {
  useBillingSubscriptionPlansQuery,
  useBillingSubscriptionQuery,
  useOrganizationSummaryQuery,
  BillingSubscriptionPlansQuery,
} from "graphql/__generated__/hooks/restapi";
import { useIsManageBillingSubscriptionAllowed } from "hooks/useIsManageBillingSubscriptionAllowed";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { processGraphQLErrorData } from "utils/apollo";
import { MILLISECONDS_IN_SECOND } from "utils/datetime";
import { ERROR_CODES } from "utils/errorCodes";
import { SPACING_2 } from "utils/layouts";
import { isNumber } from "utils/validation";
import { CardLoadingSkeleton, EnterprisePlanCard, SubscriptionCard, ProPlanCard } from "./components/Cards";
import { STRIPE_PLAN_NAME } from "./constants";

type BillingPlan = BillingSubscriptionPlansQuery["billingSubscriptionPlans"][number];

const hasRequiredPlanFields = (plan: BillingPlan | undefined): plan is BillingPlan & { price: number; currency: string } =>
  !!plan && isNumber(plan.price) && typeof plan.currency === "string";

const useData = () => {
  const { organizationId } = useOrganizationInfo();

  const {
    data: subscriptionPlansData,
    loading: plansLoading,
    error: plansError,
  } = useBillingSubscriptionPlansQuery({
    variables: {
      organizationId,
    },
  });

  const {
    data: subscriptionData,
    loading: subscriptionLoading,
    error: subscriptionError,
  } = useBillingSubscriptionQuery({
    variables: {
      organizationId,
    },
    pollInterval: 30 * MILLISECONDS_IN_SECOND,
    context: {
      suppressAlertForErrorCodes: [ERROR_CODES.OE0002],
    },
  });
  const {
    data: organizationSummaryData,
    loading: organizationSummaryLoading,
    error: organizationSummaryError,
  } = useOrganizationSummaryQuery({
    variables: {
      organizationId,
      params: {
        entity: ["month_expenses", "cloud_accounts", "employees"],
      },
    },
  });

  return {
    loading: {
      plans: plansLoading,
      subscription: subscriptionLoading,
      organizationSummary: organizationSummaryLoading,
    },
    error: {
      plans: plansError,
      subscription: subscriptionError,
      organizationSummary: organizationSummaryError,
    },
    data: {
      billingSubscriptionPlans: subscriptionPlansData?.billingSubscriptionPlans,
      billingSubscription: subscriptionData?.billingSubscription,
      organizationSummary: organizationSummaryData?.organizationSummary,
    },
  };
};

const BillingSubscription = () => {
  const isManageBillingSubscriptionAllowed = useIsManageBillingSubscriptionAllowed();

  const {
    loading,
    error,
    data: { billingSubscriptionPlans, billingSubscription, organizationSummary },
  } = useData();

  const isLoading = loading.plans || loading.subscription || loading.organizationSummary;
  const isError = error.plans || error.subscription || error.organizationSummary;
  const noData = !billingSubscriptionPlans || !billingSubscription || !organizationSummary;

  if (isLoading) {
    return <CardLoadingSkeleton />;
  }

  if (error.subscription?.graphQLErrors) {
    const errorsData = error.subscription?.graphQLErrors.map(processGraphQLErrorData);
    if (errorsData.some(({ errorCode }) => errorCode === ERROR_CODES.OE0002)) {
      return <FormattedMessage id="subscriptionCreationInProgress" />;
    }
  }

  if (isError || noData) {
    return <SomethingWentWrong />;
  }

  if (billingSubscription.plan.default && isManageBillingSubscriptionAllowed) {
    const monthlyProPlan = billingSubscriptionPlans.find((plan) => plan.name === STRIPE_PLAN_NAME.PRO_MONTHLY);
    const annualProPlan = billingSubscriptionPlans.find((plan) => plan.name === STRIPE_PLAN_NAME.PRO_YEARLY);

    const isProPlanCardVisible = hasRequiredPlanFields(monthlyProPlan) && hasRequiredPlanFields(annualProPlan);

    return (
      <Stack spacing={SPACING_2}>
        <Box display="flex" gap={SPACING_2} flexWrap="wrap">
          <SubscriptionCard billingSubscription={billingSubscription} organizationSummary={organizationSummary} />
          {isProPlanCardVisible && (
            <ProPlanCard
              monthlyPlan={{
                id: monthlyProPlan.id,
                price: monthlyProPlan.price,
                currency: monthlyProPlan.currency,
              }}
              annualPlan={{
                id: annualProPlan.id,
                price: annualProPlan.price,
                currency: annualProPlan.currency,
              }}
            />
          )}
          <EnterprisePlanCard />
        </Box>
      </Stack>
    );
  }

  return <SubscriptionCard billingSubscription={billingSubscription} organizationSummary={organizationSummary} />;
};

export default BillingSubscription;
