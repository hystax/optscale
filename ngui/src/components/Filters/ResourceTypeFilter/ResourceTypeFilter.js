import React from "react";
import { FormattedMessage } from "react-intl";
import ResourceTypeLabel from "components/ResourceTypeLabel";
import { sortObjects } from "utils/arrays";
import { OPTSCALE_RESOURCE_TYPES, RESOURCE_TYPE_BE_FILTER, RESOURCE_TYPE_FILTER } from "utils/constants";
import Filter from "../Filter";

const getRegularResourceType = (typeName) => [typeName, OPTSCALE_RESOURCE_TYPES.REGULAR].join(":");

const INSTANCE = "Instance";
const INSTANCE_REGULAR = getRegularResourceType(INSTANCE);

const VOLUME = "Volume";
const VOLUME_REGULAR = getRegularResourceType(VOLUME);

class ResourceTypeFilter extends Filter {
  static filterName = RESOURCE_TYPE_FILTER;

  static apiName = RESOURCE_TYPE_BE_FILTER;

  static displayedName = (<FormattedMessage id="resourceType" />);

  static _getValue(filterItem) {
    return `${filterItem.name}:${filterItem.type}`;
  }

  static _getDisplayedValueRenderer(filterItem) {
    return (
      <ResourceTypeLabel
        resourceInfo={{
          resourceType: filterItem.name,
          clusterTypeId: filterItem.type === OPTSCALE_RESOURCE_TYPES.CLUSTER,
          isEnvironment: filterItem.type === OPTSCALE_RESOURCE_TYPES.ENVIRONMENT
        }}
      />
    );
  }

  suggestions = [
    {
      name: this.constructor.filterName,
      value: INSTANCE_REGULAR,
      label: this.constructor._getDisplayedValueRenderer({
        name: INSTANCE,
        type: OPTSCALE_RESOURCE_TYPES.REGULAR
      })
    },
    {
      name: this.constructor.filterName,
      value: VOLUME_REGULAR,
      label: this.constructor._getDisplayedValueRenderer({
        name: VOLUME,
        type: OPTSCALE_RESOURCE_TYPES.REGULAR
      })
    }
  ];

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

export default ResourceTypeFilter;
