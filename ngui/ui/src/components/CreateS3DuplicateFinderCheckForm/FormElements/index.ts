import BucketsField, { FIELD_NAME as BUCKETS_FIELD_NAME } from "./BucketsField";
import DataSourcesField, { FIELD_NAME as DATA_SOURCES_FIELD_NAME } from "./DataSourcesField";
import SizeField, { FIELD_NAME as SIZE_FIELD_NAME } from "./SizeField";

const FIELD_NAMES = Object.freeze({
  BUCKETS_FIELD_NAME,
  SIZE_FIELD_NAME,
  DATA_SOURCES_FIELD_NAME
});

export { DataSourcesField, BucketsField, BUCKETS_FIELD_NAME, SizeField, FIELD_NAMES };
