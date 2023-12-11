import DataSourcesField, { FIELD_NAME as DATA_SOURCES_FIELD_NAME } from "./DataSourcesField";
import FiltersField, { FIELD_NAME as FILTERS_FIELD_NAME } from "./FiltersField";
import FormButtons from "./FormButtons";
import InstancesField, { FIELD_NAME as INSTANCES_FIELD_NAME } from "./InstancesField";

const FIELD_NAMES = Object.freeze({
  INSTANCES_FIELD_NAME,
  DATA_SOURCES_FIELD_NAME,
  FILTERS_FIELD_NAME
});

export { DataSourcesField, InstancesField, FiltersField, FormButtons, FIELD_NAMES };
