import { useTheme } from "@mui/material/styles";
import { useIntl } from "react-intl";
import { SI_UNITS, useFormatDigitalUnit } from "components/FormattedDigitalUnit";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { getAverageLineValue, getTotalLineValue } from "utils/charts";
import { METRIC_TYPES } from "utils/constants";
import { CHART_VALUE_TYPES } from "./constants";
import getChartProps from "./getChartProps";

const getLinesWithMarkerData = (metrics, definitionGetters) =>
  Object.entries(metrics).map(([metricName, metricLineData]) => {
    const getDefinition = definitionGetters[metricName];
    return getDefinition(metricLineData);
  });

const cpuMetricChartProps = ({ metricType, metrics, colors, intl }) => {
  const getCpuMetricLineDefinition = (data) => {
    const formattedData = data.map((d) => ({ ...d, y: d.y / 100 }));
    return {
      line: {
        id: "cpu",
        data: formattedData
      },
      markerData: {
        name: "cpuAverage",
        value: getAverageLineValue(formattedData),
        dataTestIdName: "cpu_average"
      }
    };
  };

  const definitionGetters = {
    cpuMetricData: getCpuMetricLineDefinition
  };

  return getChartProps({
    metricType,
    valueType: CHART_VALUE_TYPES.PERCENT,
    linesWithMarkerData: getLinesWithMarkerData(metrics, definitionGetters),
    colors,
    formatYValue: (value) =>
      intl.formatNumber(value, {
        format: "percentage",
        maximumFractionDigits: 1
      })
  });
};

const memoryMetricChartProps = ({ metricType, metrics, colors, intl }) => {
  const getMemoryMetricLineDefinition = (data) => {
    const formattedData = data.map((d) => ({ ...d, y: d.y / 100 }));
    return {
      line: {
        id: "memory",
        data: formattedData
      },
      markerData: {
        name: "memoryAverage",
        value: getAverageLineValue(formattedData),
        dataTestIdName: "memory_average"
      }
    };
  };

  const definitionGetters = {
    memoryMetricData: getMemoryMetricLineDefinition
  };

  return getChartProps({
    metricType,
    valueType: CHART_VALUE_TYPES.PERCENT,
    linesWithMarkerData: getLinesWithMarkerData(metrics, definitionGetters),
    colors,
    formatYValue: (value) =>
      intl.formatNumber(value, {
        format: "percentage",
        maximumFractionDigits: 1
      })
  });
};

const diskOperationsChartProps = ({ metricType, metrics, colors, intl }) => {
  const getReadMetricLineDefinition = (data) => ({
    line: {
      id: "read",
      data
    },
    markerData: {
      name: "readAverage",
      value: getAverageLineValue(data),
      dataTestIdName: "disk_read_average"
    }
  });

  const getWriteMetricLineDefinition = (data) => ({
    line: {
      id: "write",
      data
    },
    markerData: {
      name: "writeAverage",
      value: getAverageLineValue(data),
      dataTestIdName: "disk_write_average"
    }
  });

  const definitionGetters = {
    readMetricData: getReadMetricLineDefinition,
    writeMetricData: getWriteMetricLineDefinition
  };

  return getChartProps({
    metricType,
    valueType: CHART_VALUE_TYPES.PER_SECOND,
    linesWithMarkerData: getLinesWithMarkerData(metrics, definitionGetters),
    colors,
    formatYValue: (value) =>
      intl.formatMessage(
        {
          id: "valuePerSec"
        },
        { value: intl.formatNumber(value, { maximumFractionDigits: 1 }) }
      )
  });
};

const networkChartProps = ({ metricType, metrics, colors, intl, formatDigitalUnit }) => {
  const getMemoryInLineDefinition = (data) => ({
    line: {
      id: "in",
      data
    },
    markerData: {
      name: "inTotal",
      value: getTotalLineValue(data),
      dataTestIdName: "network_in_total"
    }
  });

  const getMemoryOutLineDefinition = (data) => ({
    line: {
      id: "out",
      data
    },
    markerData: {
      name: "outTotal",
      value: getTotalLineValue(data),
      dataTestIdName: "network_out_total"
    }
  });

  const definitionGetters = {
    memoryInMetricData: getMemoryInLineDefinition,
    memoryOutMetricData: getMemoryOutLineDefinition
  };

  return getChartProps({
    metricType,
    valueType: CHART_VALUE_TYPES.IEC_BYTE_PER_SECOND,
    linesWithMarkerData: getLinesWithMarkerData(metrics, definitionGetters),
    colors,
    formatYValue: (value) =>
      intl.formatMessage(
        {
          id: "valuePerSec"
        },
        {
          value: formatDigitalUnit({
            value,
            baseUnit: SI_UNITS.BYTE,
            maximumFractionDigits: 1
          })
        }
      )
  });
};

const convertMetricDataToLineData = (metricData) =>
  metricData.map(({ date, value }) => ({
    x: date,
    y: value
  }));

const getMetricsLineData = (metrics) => {
  const notEmptyMetricLines = Object.entries(metrics)
    .filter(([, metricData]) => !isEmptyArray(metricData))
    .map(([metricKey, metricData]) => [metricKey, convertMetricDataToLineData(metricData)]);
  const allXPointValues = [...new Set(notEmptyMetricLines.flatMap(([, line]) => line.map((l) => l.x)).sort())];

  const fillLineDataWithNullPoints = (line) =>
    allXPointValues.map((x) => {
      const point = line.find((p) => p.x === x);
      return point || { x, y: null };
    });

  return Object.fromEntries(notEmptyMetricLines.map(([name, line]) => [name, fillLineDataWithNullPoints(line)]));
};

const useChartPropsByMetricType = (metricType, metrics) => {
  const metricsLineData = getMetricsLineData(metrics);

  const theme = useTheme();
  const colors = theme.palette.chart;
  const intl = useIntl();
  const formatDigitalUnit = useFormatDigitalUnit();

  if (metricType === METRIC_TYPES.CPU) {
    return cpuMetricChartProps({ metricType, metrics: metricsLineData, colors, intl });
  }
  if (metricType === METRIC_TYPES.MEMORY) {
    return memoryMetricChartProps({ metricType, metrics: metricsLineData, colors, intl });
  }
  if (metricType === METRIC_TYPES.DISK_IO) {
    return diskOperationsChartProps({ metricType, metrics: metricsLineData, colors, intl });
  }
  if (metricType === METRIC_TYPES.NETWORK) {
    return networkChartProps({ metricType, metrics: metricsLineData, colors, intl, formatDigitalUnit });
  }

  throw new Error("Unknown metric type");
};

export default useChartPropsByMetricType;
