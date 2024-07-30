export const FIELD_NAMES = Object.freeze({
  NAME: "name",
  SELECTED_DATASETS: "selectedDatasets",
  RUN_TAGS_FIELD_NAME: "runTags",
  GROUP_BY_HYPERPARAMETERS_FIELD_NAME: "groupByHyperparameters",
  PRIMARY_METRIC_FIELD_NAME: "primaryMetric",
  SECONDARY_METRICS_FIELD_NAME: "secondaryMetrics",
  METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES: Object.freeze({
    NAME: "metricRestrictions",
    ARRAY_FIELD_NAMES: Object.freeze({
      METRIC_MIN: "min",
      METRIC_MAX: "max",
      METRIC: "metric"
    })
  }),
  DATASETS_COVERAGE_ARRAY_FIELD_NAMES: Object.freeze({
    NAME: "datasetsCoverage",
    ARRAY_FIELD_NAMES: Object.freeze({
      DATASET_LABEL: "datasetLabel",
      LAST_DATASETS_COVERED: "lastDatasetsCovered"
    })
  })
});
