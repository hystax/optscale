import React from "react";
import Grid from "@mui/material/Grid";
import useMetric from "hooks/useMetric";
import { isEmptyArray } from "utils/arrays";
import { METRIC_TYPES } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import MetricCard from "./MetricCard";

const GridItem = ({ children }: { children: React.ReactNode }) => (
  <Grid xs={12} sm={6} md={6} lg={4} xl={3} item>
    {children}
  </Grid>
);

const ResourceMetrics = ({ metrics, isLoading = false }) => {
  const cpuMetric = useMetric(METRIC_TYPES.CPU, { cpuMetricData: metrics.cpu });
  const memoryMetric = useMetric(METRIC_TYPES.MEMORY, { memoryMetricData: metrics.ram });
  const diskOperationsMetric = useMetric(METRIC_TYPES.DISK_IO, {
    readMetricData: metrics.disk_read_io,
    writeMetricData: metrics.disk_write_io,
  });
  const networkMetric = useMetric(METRIC_TYPES.NETWORK, {
    memoryInMetricData: metrics.network_in_io,
    memoryOutMetricData: metrics.network_out_io,
  });
  const bytesSentMetric = useMetric(METRIC_TYPES.BYTES_SENT, {
    bytesSentMetricData: metrics.bytes_sent,
  });
  const packetsSentMetric = useMetric(METRIC_TYPES.PACKETS_SENT, {
    packetsSentMetricData: metrics.packets_sent,
  });
  const diskIOUsageMetric = useMetric(METRIC_TYPES.DISK_IO_USAGE, {
    diskIOUsageMetricData: metrics.disk_io_usage,
  });
  const consolidatedDiskIOMetric = useMetric(METRIC_TYPES.CONSOLIDATED_DISK_IO, {
    consolidatedDiskIOMetricData: metrics.disk_io,
  });
  const requestsMetric = useMetric(METRIC_TYPES.REQUESTS, {
    requestsMetricData: metrics.requests,
  });

  return (
    <Grid container spacing={SPACING_2}>
      {isLoading ? (
        <>
          {[...new Array(4).keys()].map((key) => (
            <GridItem key={key}>
              <MetricCard isLoading />
            </GridItem>
          ))}
        </>
      ) : (
        [
          cpuMetric,
          memoryMetric,
          diskOperationsMetric,
          networkMetric,
          bytesSentMetric,
          packetsSentMetric,
          diskIOUsageMetric,
          consolidatedDiskIOMetric,
          requestsMetric,
        ]
          .filter((metric) => !isEmptyArray(metric.chartProps.lines))
          .map((metric) => (
            <GridItem key={metric.type}>
              <MetricCard title={metric.title} chartProps={metric.chartProps} dataTestIds={metric.cardDataTestIds} />
            </GridItem>
          ))
      )}
    </Grid>
  );
};

export default ResourceMetrics;
