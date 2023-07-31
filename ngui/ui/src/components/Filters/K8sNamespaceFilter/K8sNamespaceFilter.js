import React from "react";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import { intl } from "translations/react-intl-config";
import { sortObjects } from "utils/arrays";
import { CLOUD_ACCOUNT_TYPES_LIST, K8S_NAMESPACE_BE_FILTER, K8S_NAMESPACE_FILTER } from "utils/constants";
import Filter from "../Filter";

class K8sNamespaceFilter extends Filter {
  static filterName = K8S_NAMESPACE_FILTER;

  static apiName = K8S_NAMESPACE_BE_FILTER;

  static displayedName = (<FormattedMessage id="k8sNamespace" />);

  static displayedNameString = intl.formatMessage({ id: "k8sNamespace" });

  // TODO: Use ajv TS integration to create schema based on types def
  static filterItemSchema = {
    type: "object",
    nullable: true,
    required: ["name", "cloud_type"],
    additionalProperties: false,
    properties: {
      name: {
        type: "string"
      },
      cloud_type: {
        type: "string",
        enum: CLOUD_ACCOUNT_TYPES_LIST
      }
    }
  };

  // TODO: Use ajv TS integration to create schema based on types def
  static appliedFilterSchema = {
    type: "string"
  };

  static _getValue(filterItem) {
    return filterItem.name;
  }

  static _getDisplayedValueRenderer(filterItem, props) {
    return <CloudLabel name={filterItem.name} type={filterItem.cloud_type} disableLink {...props} />;
  }

  static _getDisplayedValueStringRenderer(filterItem) {
    return filterItem.name;
  }

  _getAppliedFilterItem(appliedFilter, filterItem) {
    return {
      value: appliedFilter,
      displayedValue: this.constructor.getDisplayedValueRenderer(filterItem, () => ({
        iconProps: {
          dataTestId: `${this.constructor.filterName}_filter_logo`
        }
      })),
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

export default K8sNamespaceFilter;
