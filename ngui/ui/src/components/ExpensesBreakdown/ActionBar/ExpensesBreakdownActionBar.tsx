import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import { EXPENSES, EXPENSES_BY_CLOUD, EXPENSES_BY_OWNER, EXPENSES_BY_POOL } from "urls";
import { COST_EXPLORER, CLOUD_DETAILS, OWNER_DETAILS, POOL_DETAILS, EXPENSES_FILTERBY_TYPES } from "utils/constants";

const ENTITY_TYPES = Object.freeze({
  CLOUD: "cloud",
  OWNER: "owner",
  POOL: "pool"
});

const getEntityTypeByBreakdownType = (expensesBreakdownType) =>
  ({
    [CLOUD_DETAILS]: ENTITY_TYPES.CLOUD,
    [OWNER_DETAILS]: ENTITY_TYPES.OWNER,
    [POOL_DETAILS]: ENTITY_TYPES.POOL
  })[expensesBreakdownType];

const getEntityTypeByFilter = (filterBy) =>
  ({
    [EXPENSES_FILTERBY_TYPES.EMPLOYEE]: ENTITY_TYPES.OWNER,
    [EXPENSES_FILTERBY_TYPES.CLOUD]: ENTITY_TYPES.CLOUD,
    [EXPENSES_FILTERBY_TYPES.POOL]: ENTITY_TYPES.POOL
  })[filterBy];

const getCostExplorerExpensesBreakdownTitle = (entityType) => (
  <FormattedMessage
    id="expensesBreakdownByTitle"
    values={{
      entityType
    }}
  />
);

const getExpensesBreakdownTitle = (name, entityType) => (
  <FormattedMessage
    id="expensesBreakdownForTitle"
    values={{
      name,
      entityType
    }}
  />
);

const ExpensesBreakdownActionBar = ({ expensesBreakdownType, filterBy, name, isLoading }) => {
  const isCostExplorerBreakdown = expensesBreakdownType === COST_EXPLORER;

  const getActionBarDefinitions = () => {
    if (isCostExplorerBreakdown) {
      const entityType = getEntityTypeByFilter(filterBy);
      const title = getCostExplorerExpensesBreakdownTitle(entityType);

      return {
        titleText: title,
        breadcrumbs: [
          <Link key={1} to={EXPENSES} component={RouterLink}>
            <FormattedMessage id="costExplorerTitle" />
          </Link>
        ]
      };
    }

    const entityType = getEntityTypeByBreakdownType(expensesBreakdownType);
    const title = getExpensesBreakdownTitle(name, entityType);

    return {
      titleText: title,
      breadcrumbs: [
        <Link key={1} to={EXPENSES} component={RouterLink}>
          <FormattedMessage id="costExplorerTitle" />
        </Link>,
        <Link
          key={2}
          to={
            {
              [ENTITY_TYPES.OWNER]: EXPENSES_BY_OWNER,
              [ENTITY_TYPES.CLOUD]: EXPENSES_BY_CLOUD,
              [ENTITY_TYPES.POOL]: EXPENSES_BY_POOL
            }[entityType]
          }
          component={RouterLink}
        >
          {getCostExplorerExpensesBreakdownTitle(entityType)}
        </Link>
      ]
    };
  };

  const { titleText, breadcrumbs } = getActionBarDefinitions();

  const actionBarData = {
    breadcrumbs,
    title: {
      text: titleText,
      isLoading
    }
  };

  return <ActionBar data={actionBarData} />;
};

export default ExpensesBreakdownActionBar;
