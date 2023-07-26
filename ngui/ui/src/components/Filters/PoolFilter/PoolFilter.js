import React from "react";
import { FormattedMessage } from "react-intl";
import PoolLabel from "components/PoolLabel";
import { intl } from "translations/react-intl-config";
import { getPoolIdWithSubPools, isPoolIdWithSubPools } from "urls";
import { sortObjects } from "utils/arrays";
import { POOL_BE_FILTER, POOL_ID_FILTER, POOL_TYPES_LIST } from "utils/constants";
import Filter from "../Filter";

class PoolFilter extends Filter {
  static filterName = POOL_ID_FILTER;

  static apiName = POOL_BE_FILTER;

  static displayedName = (<FormattedMessage id="pool" />);

  static displayedNameString = intl.formatMessage({ id: "pool" });

  static enablePopoverCheckbox = true;

  static checkboxLabel = (<FormattedMessage id="withSubPools" />);

  // TODO: Use ajv TS integration to create schema based on types def
  static filterItemSchema = {
    type: "object",
    required: ["id", "name", "purpose"],
    additionalProperties: false,
    properties: {
      id: {
        type: "string"
      },
      name: {
        type: "string"
      },
      purpose: {
        type: "string",
        enum: POOL_TYPES_LIST
      }
    }
  };

  // TODO: Use ajv TS integration to create schema based on types def
  static appliedFilterSchema = {
    type: "string"
  };

  static _getValue(filterItem) {
    return filterItem.id;
  }

  static _getDisplayedValueRenderer(filterItem, props) {
    return <PoolLabel name={filterItem.name} type={filterItem.purpose} disableLink {...props} />;
  }

  static _getDisplayedValueStringRenderer(filterItem, props) {
    const { withSubPools } = props;

    if (withSubPools) {
      return `${filterItem.name} ${intl.formatMessage({ id: "(withSubPools)" })}`;
    }

    return filterItem.name;
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
        withSubpools: isPoolIdWithSubPools(appliedFilter)
      })),
      displayedValueString: this.constructor.getDisplayedValueStringRenderer(filterItem, () => ({
        withSubPools: isPoolIdWithSubPools(appliedFilter)
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
