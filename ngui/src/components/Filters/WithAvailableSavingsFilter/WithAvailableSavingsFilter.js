import React from "react";
import { FormattedMessage } from "react-intl";
import { intl } from "translations/react-intl-config";
import { AVAILABLE_SAVINGS_FILTER, RECOMMENDATIONS_BE_FILTER } from "utils/constants";
import Filter from "../Filter";

class WithAvailableSavingsFilter extends Filter {
  static filterName = AVAILABLE_SAVINGS_FILTER;

  static apiName = RECOMMENDATIONS_BE_FILTER;

  static displayedName = (<FormattedMessage id="withAvailableSavings" />);

  static displayedNameString = intl.formatMessage({ id: "withAvailableSavings" });

  // TODO: Use ajv TS integration to create schema based on types def
  static filterItemSchema = {
    type: "boolean"
  };

  // TODO: Use ajv TS integration to create schema based on types def
  static appliedFilterSchema = {
    type: "boolean"
  };

  static _getValue(filterItem) {
    return filterItem;
  }

  static _getDisplayedValueRenderer(filterItem) {
    return intl.formatMessage({ id: filterItem ? "yes" : "no" });
  }

  static _getDisplayedValueStringRenderer(filterItem) {
    return intl.formatMessage({ id: filterItem ? "yes" : "no" });
  }

  _getAppliedFilterItem(appliedFilter, filterItem) {
    return {
      value: appliedFilter,
      displayedValue: this.constructor.getDisplayedValueRenderer(filterItem),
      displayedValueString: this.constructor.getDisplayedValueStringRenderer(filterItem)
    };
  }
}

export default WithAvailableSavingsFilter;
