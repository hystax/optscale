import React from "react";
import { FormattedMessage } from "react-intl";
import { sortObjects } from "utils/arrays";
import { GOALS_BE_FILTER, GOALS_FILTER } from "utils/constants";
import Filter from "../Filter";

class GoalsFilter extends Filter {
  static filterName = GOALS_FILTER;

  static apiName = GOALS_BE_FILTER;

  static displayedName = (<FormattedMessage id="goals" />);

  static _getValue(filterItem) {
    return filterItem.value;
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
