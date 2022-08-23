import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import { COST_EXPLORER, CLOUD_DETAILS, OWNER_DETAILS, POOL_DETAILS, EXPENSES_FILTERBY_TYPES } from "utils/constants";

const getEntityTypeByBreakdownType = (expensesBreakdownType) =>
  ({
    [CLOUD_DETAILS]: "cloud",
    [OWNER_DETAILS]: "owner",
    [POOL_DETAILS]: "pool"
  }[expensesBreakdownType]);

const getEntityTypeByFilter = (filterBy) =>
  ({
    [EXPENSES_FILTERBY_TYPES.EMPLOYEE]: "owner",
    [EXPENSES_FILTERBY_TYPES.CLOUD]: "cloud",
    [EXPENSES_FILTERBY_TYPES.POOL]: "pool"
  }[filterBy]);

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

  const title = isCostExplorerBreakdown
    ? getCostExplorerExpensesBreakdownTitle(getEntityTypeByFilter(filterBy))
    : getExpensesBreakdownTitle(name, getEntityTypeByBreakdownType(expensesBreakdownType));

  const actionBarData = {
    goBack: !isCostExplorerBreakdown,
    title: {
      text: title,
      isLoading
    }
  };

  return <ActionBar data={actionBarData} />;
};

ExpensesBreakdownActionBar.propTypes = {
  filterBy: PropTypes.string,
  isLoading: PropTypes.bool,
  name: PropTypes.string,
  expensesBreakdownType: PropTypes.oneOf([COST_EXPLORER, CLOUD_DETAILS, OWNER_DETAILS, POOL_DETAILS])
};

export default ExpensesBreakdownActionBar;
