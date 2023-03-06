import React from "react";
import { FormattedMessage } from "react-intl";
import { sortObjects } from "utils/arrays";
import { GOALS_BE_FILTER, GOALS_FILTER, GOALS_FILTER_TYPES, GOAL_STATUS } from "utils/constants";
import Filter from "../Filter";

const checkGoalsMet = (parameters) =>
  Object.values(parameters)
    .filter(({ value }) => value !== undefined)
    .every(({ tendency, targetValue, value }) => {
      if (tendency === GOALS_FILTER_TYPES.LESS_IS_BETTER) {
        return value <= targetValue;
      }
      return value > targetValue;
    });

const checkGoalsNotMet = (parameters) =>
  Object.values(parameters)
    .filter(({ value }) => value !== undefined)
    .some(({ tendency, targetValue, value }) => {
      if (tendency === GOALS_FILTER_TYPES.LESS_IS_BETTER) {
        return value >= targetValue;
      }
      return value < targetValue;
    });

export const checkGoalsFilter = {
  [GOAL_STATUS.MET]: (parameters) => checkGoalsMet(parameters),
  [GOAL_STATUS.NOT_MET]: (parameters) => checkGoalsNotMet(parameters)
};

class GoalsFilter extends Filter {
  static filterName = GOALS_FILTER;

  static apiName = GOALS_BE_FILTER;

  static displayedName = (<FormattedMessage id="goals" />);

  static _getValue(filterItem) {
    return filterItem.name;
  }

  static _getDisplayedValueRenderer(filterItem) {
    return <FormattedMessage id={filterItem.name} />;
  }

  _getAppliedFilterItem(appliedFilter, filterItem) {
    return {
      value: appliedFilter,
      displayedValue: this.constructor.getDisplayedValueRenderer(filterItem)
    };
  }

  static _sortFilterValues(items) {
    return sortObjects({
      array: items,
      field: "name",
      type: "asc"
    });
  }
}

export default GoalsFilter;
