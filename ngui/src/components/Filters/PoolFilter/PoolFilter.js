import React from "react";
import { FormattedMessage } from "react-intl";
import PoolLabel from "components/PoolLabel";
import { getPoolIdWithSubPools, isPoolIdWithSubPools } from "urls";
import { sortObjects } from "utils/arrays";
import { POOL_BE_FILTER, POOL_ID_FILTER } from "utils/constants";
import Filter from "../Filter";

class PoolFilter extends Filter {
  static filterName = POOL_ID_FILTER;

  static apiName = POOL_BE_FILTER;

  static displayedName = (<FormattedMessage id="pool" />);

  static enablePopoverCheckbox = true;

  static checkboxLabel = (<FormattedMessage id="withSubPools" />);

  static _getValue(filterItem) {
    return filterItem.id;
  }

  static _getDisplayedValueRenderer(filterItem, props) {
    return <PoolLabel name={filterItem.name} type={filterItem.purpose} disableLink {...props} />;
  }

  findFilterValue(value) {
    return this.filterValues.find((item) => {
      const filterValue = this.constructor.getValue(item);
      return filterValue === value || getPoolIdWithSubPools(filterValue) === value;
    });
  }

  _getAppliedFilterItem(appliedFilter, filterItem) {
    return {
      value: appliedFilter,
      displayedValue: this.constructor.getDisplayedValueRenderer(filterItem, () => ({
        id: filterItem.id,
        disableLink: false,
        dataTestId: `${this.constructor.filterName}_filter_link`,
        iconProps: {
          dataTestId: `${this.constructor.filterName}_filter_logo`
        },
        name: (
          <>
            {filterItem.name}
            &nbsp;
            {isPoolIdWithSubPools(appliedFilter) && <FormattedMessage id="(withSubPools)" />}
          </>
        )
      }))
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

export default PoolFilter;
