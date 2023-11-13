import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { getResourceUrl } from "urls";
import { FORMATTED_MONEY_TYPES, RESOURCE_PAGE_TABS } from "../../utils/constants";
import FormattedMoney from "../FormattedMoney";
import ResourceLink from "../ResourceLink";

const ExpenseCell = ({ rowData, id }) => {
  const { saving, cluster_type_id: clusterTypeId, resource_id: resourceId, cost } = rowData;
  let savings = null;
  if (saving) {
    const savingMessage = (
      <FormattedMessage
        id="possibleMonthlySavingsWithValue"
        values={{
          value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={saving} />
        }}
      />
    );
    // Temporary disable link to the Recommendations tab for cluster resources
    // see "Further improvements" - https://datatrendstech.atlassian.net/wiki/spaces/OPT/pages/2078998612/Clusters+-+step+1#Further-improvements
    savings = clusterTypeId ? (
      <Typography variant="caption">{savingMessage}</Typography>
    ) : (
      <Link to={`${getResourceUrl(resourceId)}?tab=${RESOURCE_PAGE_TABS.RECOMMENDATIONS}`} component={RouterLink}>
        <Typography variant="caption">{savingMessage}</Typography>
      </Link>
    );
  }
  return (
    <div>
      <ResourceLink dataTestId={`resource_expenses_${id}`} resourceId={resourceId} tabName={RESOURCE_PAGE_TABS.EXPENSES}>
        <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cost} />
      </ResourceLink>
      <br />
      {savings}
    </div>
  );
};

export default ExpenseCell;
