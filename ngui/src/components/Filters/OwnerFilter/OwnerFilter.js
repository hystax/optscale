import React from "react";
import { FormattedMessage } from "react-intl";
import { sortObjects } from "utils/arrays";
import { OWNER_BE_FILTER, OWNER_ID_FILTER } from "utils/constants";
import Filter from "../Filter";

class OwnerFilter extends Filter {
  static filterName = OWNER_ID_FILTER;

  static apiName = OWNER_BE_FILTER;

  static displayedName = (<FormattedMessage id="owner" />);

  suggestions = [
    {
      name: this.constructor.filterName,
      value: this.scopeInfo.currentEmployeeId,
      label: <FormattedMessage id="assignedToMe" />
    }
  ];

  static _getValue(filterItem) {
    return filterItem.id;
  }

  static _getDisplayedValueRenderer(filterItem) {
    return filterItem.name;
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

export default OwnerFilter;
