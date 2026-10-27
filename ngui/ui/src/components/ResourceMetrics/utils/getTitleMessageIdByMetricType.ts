import { METRIC_TYPES } from "utils/constants";

const getTitleMessageIdByMetricType = (metricType: string) =>
  (
    ({
      [METRIC_TYPES.CPU]: "cpu",
      [METRIC_TYPES.MEMORY]: "memory",
      [METRIC_TYPES.DISK_IO]: "diskIO",
      [METRIC_TYPES.NETWORK]: "network",
      [METRIC_TYPES.BYTES_SENT]: "bytesSent",
      [METRIC_TYPES.PACKETS_SENT]: "packetsSent",
      [METRIC_TYPES.DISK_IO_USAGE]: "diskIOUsage",
      [METRIC_TYPES.CONSOLIDATED_DISK_IO]: "diskIO",
      [METRIC_TYPES.REQUESTS]: "requests",
    }) as const
  )[metricType];

export default getTitleMessageIdByMetricType;
