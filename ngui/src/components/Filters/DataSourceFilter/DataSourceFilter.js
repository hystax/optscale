import React from "react";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import { sortObjects } from "utils/arrays";
import { CLOUD_ACCOUNT_BE_FILTER, CLOUD_ACCOUNT_ID_FILTER } from "utils/constants";
import Filter from "../Filter";

class DataSourceFilter extends Filter {
  static filterName = CLOUD_ACCOUNT_ID_FILTER;

  static apiName = CLOUD_ACCOUNT_BE_FILTER;

  static displayedName = (<FormattedMessage id="dataSource" />);

  static _getValue(filterItem) {
    return filterItem.id;
  }

  static _getDisplayedValueRenderer(filterItem, props) {
    return <CloudLabel name={filterItem.name} type={filterItem.type} disableLink {...props} />;
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
        }
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

export default DataSourceFilter;
