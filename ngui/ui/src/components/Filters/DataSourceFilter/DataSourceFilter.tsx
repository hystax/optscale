import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import { intl } from "translations/react-intl-config";
import { sortObjects } from "utils/arrays";
import { CLOUD_ACCOUNT_BE_FILTER, CLOUD_ACCOUNT_ID_FILTER, CLOUD_ACCOUNT_TYPES_LIST } from "utils/constants";
import Filter from "../Filter";

class DataSourceFilter extends Filter {
  static filterName = CLOUD_ACCOUNT_ID_FILTER;

  static apiName = CLOUD_ACCOUNT_BE_FILTER;

  static displayedName = (<FormattedMessage id="dataSource" />);

  static displayedNameString = intl.formatMessage({ id: "dataSource" });

  // TODO: Use ajv TS integration to create schema based on types def
  static filterItemSchema = {
    type: "object",
    required: ["id", "name", "type"],
    nullable: true,
    additionalProperties: false,
    properties: {
      id: {
        type: "string"
      },
      name: {
        type: "string"
      },
      type: {
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
    return filterItem.id;
  }

  static _getDisplayedValueRenderer(filterItem, props) {
    return <CloudLabel name={filterItem.name} type={filterItem.type} disableLink {...props} />;
  }

  static _getDisplayedValueStringRenderer(filterItem) {
    return filterItem.name;
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

export default DataSourceFilter;
