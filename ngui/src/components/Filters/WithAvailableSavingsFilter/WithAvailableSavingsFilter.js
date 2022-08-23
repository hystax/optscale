import React from "react";
import { FormattedMessage } from "react-intl";
import { intl } from "translations/react-intl-config";
import { AVAILABLE_SAVINGS_FILTER, RECOMMENDATIONS_BE_FILTER } from "utils/constants";
import Filter from "../Filter";

class WithAvailableSavingsFilter extends Filter {
  static filterName = AVAILABLE_SAVINGS_FILTER;

  static apiName = RECOMMENDATIONS_BE_FILTER;

  static displayedName = (<FormattedMessage id="withAvailableSavings" />);

  static _getValue(filterItem) {
    return filterItem;
  }

  static _getDisplayedValueRenderer(filterItem) {
    return intl.formatMessage({ id: filterItem ? "yes" : "no" });
  }

  _getAppliedFilterItem(appliedFilter, filterItem) {
    return {
      value: appliedFilter,
      displayedValue: this.constructor.getDisplayedValueRenderer(filterItem)
    };
  }
}

export default WithAvailableSavingsFilter;
