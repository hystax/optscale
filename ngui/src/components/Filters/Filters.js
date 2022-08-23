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

  getAppliedValues() {
    return this.filters.flatMap((filter) => {
      const appliedFilterItems = filter.getAppliedFilterItems();

      return appliedFilterItems.map((appliedFilterItem) => ({
        name: filter.constructor.filterName,
        displayedName: filter.constructor.displayedName,
        value: appliedFilterItem.value,
        displayedValue: appliedFilterItem.displayedValue
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
}

export default Filters;
