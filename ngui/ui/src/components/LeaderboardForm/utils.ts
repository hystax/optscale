import { FIELD_NAMES } from "./constants";
import { FormValues, GetDefaultValuesParams } from "./types";

export const getDefaultValues = ({
  name,
  selectedDatasets,
  tags,
  groupByHyperparameters,
  primaryMetric,
  secondaryMetrics,
  metricRestrictions,
  datasetCoverageRules
}: GetDefaultValuesParams = {}): FormValues => ({
  [FIELD_NAMES.NAME]: name ?? "",
  [FIELD_NAMES.SELECTED_DATASETS]: selectedDatasets ?? [],
  [FIELD_NAMES.RUN_TAGS_FIELD_NAME]: tags ?? [],
  [FIELD_NAMES.GROUP_BY_HYPERPARAMETERS_FIELD_NAME]: groupByHyperparameters ?? false,
  [FIELD_NAMES.PRIMARY_METRIC_FIELD_NAME]: primaryMetric
    ? {
        id: primaryMetric.id,
        name: primaryMetric.name
      }
    : "",
  [FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME]: secondaryMetrics
    ? secondaryMetrics.map((secondaryMetric) => ({
        id: secondaryMetric.id,
        name: secondaryMetric.name
      }))
    : [],
  [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.NAME]: metricRestrictions
    ? metricRestrictions
        .map(({ max, min, id }) => ({
          [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC_MIN]:
            min === undefined || min === null ? "" : String(min),
          [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC_MAX]:
            max === undefined || max === null ? "" : String(max),
          [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC]: id
        }))
        .filter(Boolean)
    : [],
  [FIELD_NAMES.DATASETS_COVERAGE_ARRAY_FIELD_NAMES.NAME]: datasetCoverageRules
    ? Object.entries(datasetCoverageRules).map(([label, lastDataCovered]) => ({
        [FIELD_NAMES.DATASETS_COVERAGE_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.DATASET_LABEL]: label,
        [FIELD_NAMES.DATASETS_COVERAGE_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.LAST_DATASETS_COVERED]: String(lastDataCovered)
      }))
    : []
});
