import { FormattedMessage } from "react-intl";
import { sortObjects } from "utils/arrays";
import { STATUS_BE_FILTER, STATUS_FILTER } from "utils/constants";
import Filter from "../Filter";

class StatusFilter extends Filter {
  static filterName = STATUS_FILTER;

  static apiName = STATUS_BE_FILTER;

  static displayedName = (<FormattedMessage id="status" />);

  static _getValue(filterItem) {
    return filterItem.name;
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

export default StatusFilter;
