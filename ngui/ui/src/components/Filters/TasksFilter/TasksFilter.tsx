import { FormattedMessage } from "react-intl";
import { sortObjects } from "utils/arrays";
import { LINEAR_SELECTOR_ITEMS_TYPES, TASKS_BE_FILTER, TASKS_FILTER } from "utils/constants";
import Filter from "../Filter";

class TasksFilter extends Filter {
  static filterName = TASKS_FILTER;

  static apiName = TASKS_BE_FILTER;

  static displayedName = (<FormattedMessage id="tasks" />);

  static type = LINEAR_SELECTOR_ITEMS_TYPES.MULTISELECT_POPOVER;

  static _getValue(filterItem) {
    return filterItem.value;
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

export default TasksFilter;
