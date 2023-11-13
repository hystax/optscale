import { FormattedMessage } from "react-intl";
import { intl } from "translations/react-intl-config";
import { CONSTRAINT_VIOLATED_BE_FILTER, CONSTRAINT_VIOLATED_FILTER } from "utils/constants";
import Filter from "../Filter";

class WithViolatedConstraintsFilter extends Filter {
  static filterName = CONSTRAINT_VIOLATED_FILTER;

  static apiName = CONSTRAINT_VIOLATED_BE_FILTER;

  static displayedName = (<FormattedMessage id="withViolatedConstraints" />);

  static displayedNameString = intl.formatMessage({ id: "withViolatedConstraints" });

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
      label: <FormattedMessage id="withViolatedConstraints" />
    }
  ];

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

export default WithViolatedConstraintsFilter;
