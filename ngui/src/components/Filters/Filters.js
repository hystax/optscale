import { isEmpty as isEmptyArray } from "utils/arrays";
import Suggestions from "./Suggestions/Suggestions";

class Filters {
  constructor({ filters, filterValues, appliedFilters = {}, scopeInfo = {} }) {
    this.filters = filters
      .map((FilterClass) => {
        if (filterValues[FilterClass.apiName] !== undefined) {
          return new FilterClass({ filterValues, appliedFilters, scopeInfo });
        }
        return undefined;
      })
      .filter(Boolean);
  }

  getFilterSelectors() {
    const suggestionsFilter = new Suggestions({
      filterValues: {
        suggestions: this.filters.flatMap((filter) => filter.getSuggestionValues())
      },
      appliedFilters: [],
      scopeInfo: this.scopeInfo
    });

    const selectors = [suggestionsFilter, ...this.filters].map((filter) => this.constructor._getSelector(filter));

    return selectors;
  }

  static _getSelector(filter) {
    return {
      name: filter.constructor.filterName,
      displayedName: filter.constructor.displayedName,
      type: filter.constructor.type,
      items: filter.getFilterItems(),
      enablePopoverCheckbox: filter.constructor.enablePopoverCheckbox,
      checkboxLabel: filter.constructor.checkboxLabel
    };
  }

  getFilterValuesAsAppliedItems() {
    return this.filters.flatMap((filter) =>
      filter.filterValues.map((item) => filter.getAppliedFilterItem(filter.constructor.getValue(item), item))
    );
  }

  getAppliedValues() {
    return this.filters.flatMap((filter) => {
      const appliedFilterItems = filter.getAppliedFilterItems();

      return appliedFilterItems.map((appliedFilterItem) => ({
        name: filter.constructor.filterName,
        displayedName: filter.constructor.displayedName,
        displayedNameString: filter.constructor.displayedNameString,
        value: appliedFilterItem.value,
        displayedValue: appliedFilterItem.displayedValue,
        displayedValueString: appliedFilterItem.displayedValueString
      }));
    });
  }

  toQueryParametersString() {
    return this.filters
      .map((filter) => {
        const queryParameterName = filter.constructor.filterName;

        const values = filter.filterValues.map((filterValue) => filter.constructor.getValue(filterValue));

        return values.map((value) => `${queryParameterName}=${encodeURIComponent(value)}`);
      })
      .join("&");
  }

  getFilterValuesForAppliedFilters() {
    return Object.fromEntries(
      this.filters
        .map((filter) => [
          filter.constructor.apiName,
          filter.appliedFilters.map((applied) => filter.findFilterValue(applied)).filter((el) => el !== undefined)
        ])
        .filter(([, values]) => !isEmptyArray(values))
    );
  }

  getAppliedFilters() {
    return Object.fromEntries(
      this.filters
        .map((filter) => [filter.constructor.filterName, filter.appliedFilters])
        .filter(([, values]) => !isEmptyArray(values))
    );
  }
}

export default Filters;
