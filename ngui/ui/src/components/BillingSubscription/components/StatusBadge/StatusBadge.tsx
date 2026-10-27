import { FormattedMessage } from "react-intl";
import Chip from "components/Chip";
import { BillingSubscriptionStatus } from "graphql/__generated__/hooks/restapi";
import { BILLING_SUBSCRIPTION_STATUS } from "../../constants";

type StatusBadgeProps = {
  status: BillingSubscriptionStatus;
};

const STATUS_BADGE_MAP = {
  [BILLING_SUBSCRIPTION_STATUS.ACTIVE]: <Chip label={<FormattedMessage id="active" />} color="success" />,
  [BILLING_SUBSCRIPTION_STATUS.LIMIT_EXCEEDED]: <Chip label={<FormattedMessage id="limitExceeded" />} color="error" />,
  [BILLING_SUBSCRIPTION_STATUS.SUSPENDED]: <Chip label={<FormattedMessage id="suspended" />} color="error" />,
};

const StatusBadge = ({ status }: StatusBadgeProps) => STATUS_BADGE_MAP[status] ?? <Chip label={status} color="info" />;

export default StatusBadge;
