import React from "react";
import { FormattedMessage } from "react-intl";
import { LINEAR_SELECTOR_ITEMS_TYPES } from "utils/constants";
import Filter from "../Filter";

class Suggestions extends Filter {
  static filterName = "suggestedFilters";

  static apiName = "suggestions";

  static displayedName = (<FormattedMessage id="suggestedFilters" />);

  static type = LINEAR_SELECTOR_ITEMS_TYPES.POPOVER;

  static _getValue(filterItem) {
    return filterItem.value;
  }

  static _getDisplayedValueRenderer(filterItem) {
    return filterItem.label;
  }

  static getName(filterItem) {
    return filterItem.name;
  }
}

export default Suggestions;
