import { METRIC_TYPES } from "utils/constants";

const getTitleMessageIdByMetricType = (metricType) =>
  ({
    [METRIC_TYPES.CPU]: "cpu",
    [METRIC_TYPES.MEMORY]: "memory",
    [METRIC_TYPES.DISK_IO]: "diskIO",
    [METRIC_TYPES.NETWORK]: "network"
  })[metricType];

export default getTitleMessageIdByMetricType;
