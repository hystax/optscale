import { FormattedMessage } from "react-intl";
import ResourceTypeLabel from "components/ResourceTypeLabel";
import { intl } from "translations/react-intl-config";
import { sortObjects } from "utils/arrays";
import { OPTSCALE_RESOURCE_TYPES, RESOURCE_TYPE_BE_FILTER, RESOURCE_TYPE_FILTER } from "utils/constants";
import Filter from "../Filter";

const getRegularResourceType = (typeName) => [typeName, OPTSCALE_RESOURCE_TYPES.REGULAR].join(":");

const INSTANCE = "Instance";
export const INSTANCE_REGULAR = getRegularResourceType(INSTANCE);

const VOLUME = "Volume";
const VOLUME_REGULAR = getRegularResourceType(VOLUME);

class ResourceTypeFilter extends Filter {
  static filterName = RESOURCE_TYPE_FILTER;

  static apiName = RESOURCE_TYPE_BE_FILTER;

  static displayedName = (<FormattedMessage id="resourceType" />);

  static displayedNameString = intl.formatMessage({ id: "resourceType" });

  // TODO: Use ajv TS integration to create schema based on types def
  static filterItemSchema = {
    type: "object",
    required: ["name", "type"],
    additionalProperties: false,
    properties: {
      name: {
        type: "string"
      },
      type: {
        type: "string",
        enum: Object.values(OPTSCALE_RESOURCE_TYPES)
      }
    }
  };

  // TODO: Use ajv TS integration to create schema based on types def
  static appliedFilterSchema = {
    type: "string"
  };

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

  static _getDisplayedValueStringRenderer(filterItem) {
    if (filterItem.type === OPTSCALE_RESOURCE_TYPES.CLUSTER) {
      return `${filterItem.name} (${intl.formatMessage({ id: "cluster" })})`;
    }
    if (filterItem.type === OPTSCALE_RESOURCE_TYPES.ENVIRONMENT) {
      return `${filterItem.name} (${intl.formatMessage({ id: "ItEnvironment" })})`;
    }
    return filterItem.name;
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
      displayedValue: this.constructor.getDisplayedValueRenderer(filterItem),
      displayedValueString: this.constructor.getDisplayedValueStringRenderer(filterItem)
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
