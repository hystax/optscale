import { ReactNode } from "react";
import { Stack } from "@mui/material";
import { BillingSubscriptionStatus } from "graphql/__generated__/hooks/restapi";
import { SPACING_2 } from "utils/layouts";
import Alerts from "../../Alerts";

type SubscriptionCardBodyProps = {
  features: ReactNode;
  status: BillingSubscriptionStatus;
  gracePeriodStart: number;
  gracePeriodDays: number;
  endDate: number;
  cancelAtPeriodEnd: boolean;
};

const SubscriptionCardBody = ({
  features,
  status,
  gracePeriodStart,
  gracePeriodDays,
  endDate,
  cancelAtPeriodEnd,
}: SubscriptionCardBodyProps) => (
  <Stack spacing={SPACING_2}>
    <Alerts
      status={status}
      gracePeriodStart={gracePeriodStart}
      gracePeriodDays={gracePeriodDays}
      endDate={endDate}
      cancelAtPeriodEnd={cancelAtPeriodEnd}
    />
    {features}
  </Stack>
);

export default SubscriptionCardBody;
