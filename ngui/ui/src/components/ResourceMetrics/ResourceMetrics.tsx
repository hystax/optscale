import Grid from "@mui/material/Grid";
import useMetric from "hooks/useMetric";
import { METRIC_TYPES } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import MetricCard from "./MetricCard";

const GridItem = ({ children }) => (
  <Grid xs={12} sm={6} md={6} lg={4} xl={3} item>
    {children}
  </Grid>
);

const ResourceMetrics = ({ metrics, isLoading = false }) => {
  const cpuMetric = useMetric(METRIC_TYPES.CPU, { cpuMetricData: metrics.cpu });
  const memoryMetric = useMetric(METRIC_TYPES.MEMORY, { memoryMetricData: metrics.ram });
  const diskOperationsMetric = useMetric(METRIC_TYPES.DISK_IO, {
    readMetricData: metrics.disk_read_io,
    writeMetricData: metrics.disk_write_io
  });
  const networkMetric = useMetric(METRIC_TYPES.NETWORK, {
    memoryInMetricData: metrics.network_in_io,
    memoryOutMetricData: metrics.network_out_io
  });

  return (
    <Grid container spacing={SPACING_2}>
      {[cpuMetric, memoryMetric, diskOperationsMetric, networkMetric].map((metric) => (
        <GridItem key={metric.type}>
          <MetricCard
            title={metric.title}
            chartProps={metric.chartProps}
            dataTestIds={metric.cardDataTestIds}
            isLoading={isLoading}
          />
        </GridItem>
      ))}
    </Grid>
  );
};

export default ResourceMetrics;
