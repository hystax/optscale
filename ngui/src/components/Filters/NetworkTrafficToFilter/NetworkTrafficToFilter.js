import React from "react";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import { sortObjects } from "utils/arrays";
import {
  ANY_NETWORK_TRAFFIC_LOCATION,
  LINEAR_SELECTOR_ITEMS_TYPES,
  NETWORK_TRAFFIC_TO_BE_FILTER,
  NETWORK_TRAFFIC_TO_FILTER
} from "utils/constants";
import Filter from "../Filter";

class NetworkTrafficToFilter extends Filter {
  static filterName = NETWORK_TRAFFIC_TO_FILTER;

  static apiName = NETWORK_TRAFFIC_TO_BE_FILTER;

  static displayedName = (<FormattedMessage id="paidNetworkTrafficTo" />);

  static type = LINEAR_SELECTOR_ITEMS_TYPES.MULTISELECT_POPOVER;

  static _getValue(filterItem) {
    if (typeof filterItem === "string") {
      return ANY_NETWORK_TRAFFIC_LOCATION;
    }

    const { name, cloud_type: cloudType } = filterItem;

    return `${name}:${cloudType}`;
  }

  static _getDisplayedValueRenderer(filterItem, props) {
    if (this._getValue(filterItem) === ANY_NETWORK_TRAFFIC_LOCATION) {
      return <FormattedMessage id="any" />;
    }

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
    const sortItems = (values) =>
      sortObjects({
        array: values,
        field: "name",
        type: "asc"
      });

    const anyNetworkTrafficLocationValueIndex = items.findIndex(
      (item) => this._getValue(item) === ANY_NETWORK_TRAFFIC_LOCATION
    );

    const isAnyNetworkTrafficLocationValueExist = anyNetworkTrafficLocationValueIndex !== 1;

    return isAnyNetworkTrafficLocationValueExist
      ? [
          items[anyNetworkTrafficLocationValueIndex],
          ...sortItems(items.filter((_, index) => index !== anyNetworkTrafficLocationValueIndex))
        ]
      : sortItems(items);
  }
}

export default NetworkTrafficToFilter;
