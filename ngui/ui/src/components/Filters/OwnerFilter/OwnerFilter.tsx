import { FormattedMessage } from "react-intl";
import { intl } from "translations/react-intl-config";
import { sortObjects } from "utils/arrays";
import { OWNER_BE_FILTER, OWNER_ID_FILTER } from "utils/constants";
import Filter from "../Filter";

class OwnerFilter extends Filter {
  static filterName = OWNER_ID_FILTER;

  static apiName = OWNER_BE_FILTER;

  static displayedName = (<FormattedMessage id="owner" />);

  static displayedNameString = intl.formatMessage({ id: "owner" });

  // TODO: Use ajv TS integration to create schema based on types def
  static filterItemSchema = {
    type: "object",
    required: ["id", "name"],
    additionalProperties: false,
    properties: {
      id: {
        type: "string"
      },
      name: {
        type: "string"
      }
    }
  };

  // TODO: Use ajv TS integration to create schema based on types def
  static appliedFilterSchema = {
    type: "string"
  };

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

  static _getDisplayedValueStringRenderer(filterItem) {
    return filterItem.name;
  }

  _getAppliedFilterItem(appliedFilter, filterItem) {
    return {
      value: appliedFilter,
      displayedValue: this.constructor.getDisplayedValueRenderer(filterItem),
      displayedValueString: this.constructor.getDisplayedValueStringRenderer(filterItem)
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
