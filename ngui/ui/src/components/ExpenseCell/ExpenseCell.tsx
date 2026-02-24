import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { Stack } from "@mui/system";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { getResourceUrl } from "urls";
import { FORMATTED_MONEY_TYPES, RESOURCE_PAGE_TABS } from "../../utils/constants";
import FormattedMoney from "../FormattedMoney";
import ResourceLink from "../ResourceLink";

type SavingsMessageProps = {
  saving: number;
  resourceId: string;
  clusterTypeId?: string;
};

type ExpenseCellProps = {
  cost: number;
  resourceId: string;
  saving?: number;
  clusterTypeId?: string;
};

const SavingsMessage = ({ saving, clusterTypeId, resourceId }: SavingsMessageProps) => {
  const savingMessage = (
    <FormattedMessage
      id="possibleMonthlySavingsWithValue"
      values={{
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={saving} />,
      }}
    />
  );

  // Temporary disable link to the Recommendations tab for cluster resources
  // see "Further improvements"
  // - https://datatrendstech.atlassian.net/wiki/spaces/OPT/pages/2078998612/Clusters+-+step+1#Further-improvements
  return clusterTypeId ? (
    <Typography variant="caption">{savingMessage}</Typography>
  ) : (
    <Link
      to={`${getResourceUrl(resourceId)}?tab=${RESOURCE_PAGE_TABS.RECOMMENDATIONS}`}
      component={RouterLink}
      variant="caption"
      sx={{ fontWeight: "normal" }}
    >
      {savingMessage}
    </Link>
  );
};

const ExpenseCell = ({ cost, saving, clusterTypeId, resourceId }: ExpenseCellProps) => {
  const resourceLink = (
    <ResourceLink
      resourceId={resourceId}
      tabName={RESOURCE_PAGE_TABS.EXPENSES}
      dataTestId={`resource_expenses_${resourceId}`}
      params={{}}
    >
      <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cost} />
    </ResourceLink>
  );

  return saving ? (
    <Stack>
      {resourceLink}
      <SavingsMessage saving={saving} clusterTypeId={clusterTypeId} resourceId={resourceId} />
    </Stack>
  ) : (
    resourceLink
  );
};

export default ExpenseCell;
