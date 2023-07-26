import { intl } from "translations/react-intl-config";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { EMPTY_UUID, LINEAR_SELECTOR_ITEMS_TYPES } from "utils/constants";

class Filter {
  static enablePopoverCheckbox = false;

  static checkboxLabel = null;

  static type = LINEAR_SELECTOR_ITEMS_TYPES.POPOVER;

  constructor({ filterValues, appliedFilters, scopeInfo }) {
    this.scopeInfo = scopeInfo;

    this.filterValues = filterValues[this.constructor.apiName] ?? [];

    this.appliedFilters = [appliedFilters[this.constructor.filterName]]
      .flat()
      .filter((appliedValue) => appliedValue !== undefined);

    this.isApplied = this.appliedFilters.length !== 0;
  }

  static getValue(filterItem) {
    if (filterItem === null) {
      return EMPTY_UUID;
    }
    return this._getValue(filterItem);
  }

  static getDisplayedValueRenderer(filterItem, getRendererProps) {
    if (filterItem === null) {
      return intl.formatMessage({ id: "notSet" });
    }

    return this._getDisplayedValueRenderer(filterItem, getRendererProps?.() ?? {});
  }

  static getDisplayedValueStringRenderer(filterItem, getRendererProps) {
    if (filterItem === null) {
      return intl.formatMessage({ id: "notSet" });
    }

    return this._getDisplayedValueStringRenderer(filterItem, getRendererProps?.() ?? {});
  }

  static getName() {
    return this.filterName;
  }

  _sortFilterValues() {
    const hasNullItem = this.filterValues.some((filterItem) => filterItem === null);

    const items = hasNullItem ? this.filterValues.filter((filterItem) => filterItem !== null) : [...this.filterValues];

    const sortedItems =
      typeof this.constructor._sortFilterValues === "function" ? this.constructor._sortFilterValues(items) : [...items].sort();

    return hasNullItem ? [null, ...sortedItems] : sortedItems;
  }

  getFilterItems() {
    return this._sortFilterValues().map((filterValue) => ({
      name: this.constructor.getName(filterValue),
      value: this.constructor.getValue(filterValue),
      label: this.constructor.getDisplayedValueRenderer(filterValue)
    }));
  }

  findFilterValue(value) {
    return this.filterValues.find((item) => this.constructor.getValue(item) === value);
  }

  getAppliedFilterItems() {
    return this.appliedFilters.map((appliedFilter) => this.getAppliedFilterItem(appliedFilter));
  }

  getAppliedFilterItem(appliedFilter) {
    const filterItem = this.findFilterValue(appliedFilter);
    const commonData = {
      name: this.constructor.filterName,
      displayedName: this.constructor.displayedName,
      displayedNameString: this.constructor.displayedNameString
    };

    if (filterItem === undefined) {
      return {
        ...commonData,
        value: appliedFilter,
        displayedValue: intl.formatMessage({ id: "notFound" }),
        displayedValueString: intl.formatMessage({ id: "notFound" })
      };
    }

    return {
      ...commonData,
      ...this._getAppliedFilterItem(appliedFilter, filterItem)
    };
  }

  getSuggestionValues() {
    return isEmptyArray(this.suggestions) || this.isApplied
      ? []
      : this.suggestions.filter(({ value }) => this.findFilterValue(value));
  }
}

export default Filter;
