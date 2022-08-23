import React from "react";
import { FormattedMessage } from "react-intl";
import { TAG_BE_FILTER, TAG_FILTER } from "utils/constants";
import Filter from "../Filter";

class TagFilter extends Filter {
  static filterName = TAG_FILTER;

  static apiName = TAG_BE_FILTER;

  static displayedName = (<FormattedMessage id="tag" />);

  static _getValue(filterItem) {
    return filterItem;
  }

  static _getDisplayedValueRenderer(filterItem) {
    return filterItem;
  }

  _getAppliedFilterItem(appliedFilter, filterItem) {
    return {
      value: appliedFilter,
      displayedValue: this.constructor.getDisplayedValueRenderer(filterItem)
    };
  }
}

export default TagFilter;
