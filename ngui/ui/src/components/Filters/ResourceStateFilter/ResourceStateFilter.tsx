import { FormattedMessage } from "react-intl";
import { intl } from "translations/react-intl-config";
import { ACTIVE_BE_FILTER, ACTIVE_FILTER } from "utils/constants";
import Filter from "../Filter";

class ResourceStateFilter extends Filter {
  static filterName = ACTIVE_FILTER;

  static apiName = ACTIVE_BE_FILTER;

  static displayedName = (<FormattedMessage id="resourceState" />);

  static displayedNameString = intl.formatMessage({ id: "resourceState" });

  // TODO: Use ajv TS integration to create schema based on types def
  static filterItemSchema = {
    type: "boolean"
  };

  // TODO: Use ajv TS integration to create schema based on types def
  static appliedFilterSchema = {
    type: "boolean"
  };

  suggestions = [
    {
      name: this.constructor.filterName,
      value: true,
      label: this.constructor._getDisplayedValueRenderer(true)
    }
  ];

  static _getValue(filterItem) {
    return filterItem;
  }

  static _getDisplayedValueRenderer(filterItem) {
    return intl.formatMessage({ id: filterItem ? "active" : "billingOnly" });
  }

  static _getDisplayedValueStringRenderer(filterItem) {
    return intl.formatMessage({ id: filterItem ? "active" : "billingOnly" });
  }

  _getAppliedFilterItem(appliedFilter, filterItem) {
    return {
      value: appliedFilter,
      displayedValue: this.constructor.getDisplayedValueRenderer(filterItem),
      displayedValueString: this.constructor.getDisplayedValueStringRenderer(filterItem)
    };
  }
}

export default ResourceStateFilter;
