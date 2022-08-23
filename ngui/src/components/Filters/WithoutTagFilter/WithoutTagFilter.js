import React from "react";
import { FormattedMessage } from "react-intl";
import { WITHOUT_TAG_BE_FILTER, WITHOUT_TAG_FILTER } from "utils/constants";
import Filter from "../Filter";

class WithoutTagFilter extends Filter {
  static filterName = WITHOUT_TAG_FILTER;

  static apiName = WITHOUT_TAG_BE_FILTER;

  static displayedName = (<FormattedMessage id="withoutTag" />);

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

export default WithoutTagFilter;
