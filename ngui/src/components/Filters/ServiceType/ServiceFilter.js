import React from "react";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import { sortObjects } from "utils/arrays";
import { SERVICE_NAME_BE_FILTER, SERVICE_NAME_FILTER } from "utils/constants";
import Filter from "../Filter";

class ServiceType extends Filter {
  static filterName = SERVICE_NAME_FILTER;

  static apiName = SERVICE_NAME_BE_FILTER;

  static displayedName = (<FormattedMessage id="service" />);

  static _getValue(filterItem) {
    return filterItem.name;
  }

  static _getDisplayedValueRenderer(filterItem, props) {
    return <CloudLabel name={filterItem.name} type={filterItem.cloud_type} disableLink {...props} />;
  }

  _getAppliedFilterItem(appliedFilter, filterItem) {
    return {
      value: appliedFilter,
      displayedValue: this.constructor.getDisplayedValueRenderer(filterItem, () => ({
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

export default ServiceType;
