import { CLOUD_ACCOUNT_ID_FILTER, LINEAR_SELECTOR_ITEMS_TYPES } from "utils/constants";
import DataSourceFilter from "../DataSourceFilter";

class DataSourceFilterMultiple extends DataSourceFilter {
  static filterName = CLOUD_ACCOUNT_ID_FILTER;

  static type = LINEAR_SELECTOR_ITEMS_TYPES.MULTISELECT_POPOVER;
}

export default DataSourceFilterMultiple;
