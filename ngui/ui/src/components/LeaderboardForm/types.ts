import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.NAME]?: string;
  [FIELD_NAMES.SELECTED_DATASETS]?: { id: string }[];
  [FIELD_NAMES.RUN_TAGS_FIELD_NAME]: string[];
  [FIELD_NAMES.GROUP_BY_HYPERPARAMETERS_FIELD_NAME]: boolean;
  [FIELD_NAMES.PRIMARY_METRIC_FIELD_NAME]:
    | {
        id: string;
        name: string;
      }
    | "";
  [FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME]: {
    id: string;
    name: string;
  }[];
  [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.NAME]: {
    metric: string;
    max: string;
    min: string;
  }[];
  [FIELD_NAMES.DATASETS_COVERAGE_ARRAY_FIELD_NAMES.NAME]: { datasetLabel: string; lastDatasetsCovered: string }[];
};

export type GetDefaultValuesParams = {
  name?: string;
  selectedDatasets?: { id: string }[];
  tags?: string[];
  groupByHyperparameters?: boolean;
  primaryMetric?: { id: string; name: string };
  secondaryMetrics?: { id: string; name: string }[];
  metricRestrictions?: { max: string | number | null | undefined; min: string | number | null | undefined; id: string }[];
  datasetCoverageRules?: { [label: string]: string | number };
};
