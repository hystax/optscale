import { useTheme } from "@mui/material/styles";
import { FormattedMessage, useIntl } from "react-intl";
import { useParams } from "react-router-dom";
import DynamicFractionDigitsValue, { useFormatDynamicFractionDigitsValue } from "components/DynamicFractionDigitsValue";
import FormattedDigitalUnit, { IEC_UNITS, formatDigitalUnit } from "components/FormattedDigitalUnit";
import FormattedMoney, { useMoneyFormatter } from "components/FormattedMoney";
import { useFormatIntervalDuration } from "hooks/useFormatIntervalDuration";
import { useTaskBreakdownState } from "reducers/taskBreakdown/useTaskBreakdownState";
import { getColorsMap } from "utils/charts";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { intervalToDuration, INTERVAL_DURATION_VALUE_TYPES } from "utils/datetime";
import Layout from "./Layout";

const BREAKDOWN_BY_QUERY_PARAMETER = "breakdownBy";

const getDurationFormatter =
  ({ formatInterval, formatMessage }) =>
  (value, { compact = false } = {}) =>
    value === 0
      ? formatMessage({ id: compact ? "xSecondsCompact" : "xSeconds" }, { x: 0 })
      : formatInterval({
          formatTo: [
            INTERVAL_DURATION_VALUE_TYPES.WEEKS,
            INTERVAL_DURATION_VALUE_TYPES.DAYS,
            INTERVAL_DURATION_VALUE_TYPES.HOURS,
            INTERVAL_DURATION_VALUE_TYPES.MINUTES,
            INTERVAL_DURATION_VALUE_TYPES.SECONDS
          ],
          duration: intervalToDuration({
            start: 0,
            end: value * 1000
          }),
          compact
        });

const METRIC_BREAKDOWN_NAME = Object.freeze({
  DURATION: "duration",
  EXPENSES: "expenses",
  TASK_CPU: "task_cpu",
  CPU_UPTIME: "cpu_uptime",
  DATA_READ: "data_read",
  DATA_WRITTEN: "data_written"
});

const Breakdown = ({ runs }) => {
  const theme = useTheme();
  const intl = useIntl();

  const { taskId } = useParams();

  const formatInterval = useFormatIntervalDuration();
  const formatDuration = getDurationFormatter({
    formatInterval,
    formatMessage: intl.formatMessage
  });
  const formatMoney = useMoneyFormatter();

  const formatDynamicFractionDigitsValue = useFormatDynamicFractionDigitsValue();

  const getMetaBreakdownConfig = () => [
    {
      name: METRIC_BREAKDOWN_NAME.DURATION,
      renderBreakdownName: () => <FormattedMessage id="duration" />,
      getPointValue: (run) => run.duration ?? null,
      formatValue: (value) => formatDuration(value),
      formatAxis: (value) =>
        formatDuration(value, {
          compact: true
        })
    },
    {
      name: METRIC_BREAKDOWN_NAME.EXPENSES,
      renderBreakdownName: () => <FormattedMessage id="expenses" />,
      getPointValue: (run) => run.cost ?? null,
      formatValue: (value) => <FormattedMoney value={value} />,
      formatAxis: (value) => formatMoney(FORMATTED_MONEY_TYPES.COMPACT, value)
    },
    {
      name: METRIC_BREAKDOWN_NAME.TASK_CPU,
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="tasksCPU" />,
      getPointValue: (run) => run.task_cpu ?? null,
      formatValue: (value) => formatDuration(value),
      formatAxis: (value) =>
        formatDuration(value, {
          compact: true
        })
    },
    {
      name: METRIC_BREAKDOWN_NAME.CPU_UPTIME,
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="cpuUptime" />,
      getPointValue: (run) => run.cpu_uptime ?? null,
      formatValue: (value) => formatDuration(value),
      formatAxis: (value) =>
        formatDuration(value, {
          compact: true
        })
    },
    {
      name: METRIC_BREAKDOWN_NAME.DATA_READ,
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="dataRead" />,
      getPointValue: (run) => run.data_read ?? null,
      formatValue: (value) => <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />,
      formatAxis: (value) =>
        formatDigitalUnit({
          value,
          baseUnit: IEC_UNITS.MEBIBYTE,
          maximumFractionDigits: 2
        })
    },
    {
      name: METRIC_BREAKDOWN_NAME.DATA_WRITTEN,
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="dataWritten" />,
      getPointValue: (run) => run.data_written ?? null,
      formatValue: (value) => <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />,
      formatAxis: (value) =>
        formatDigitalUnit({
          value,
          baseUnit: IEC_UNITS.MEBIBYTE,
          maximumFractionDigits: 2
        })
    }
  ];

  const getMetricsBreakdownConfig = () => {
    const metricBreakdownKeyNameMap = Object.fromEntries(
      runs.filter(({ metrics }) => !!metrics).flatMap((run) => run.metrics.map(({ key, name }) => [key, name]))
    );

    return Object.entries(metricBreakdownKeyNameMap).map(([key, name]) => ({
      name: key,
      renderBreakdownName: () => name,
      getPointValue: (run) => run.data?.[key] ?? null,
      formatValue: (value) => <DynamicFractionDigitsValue value={value} maximumFractionDigits={2} />,
      formatAxis: (value) =>
        formatDynamicFractionDigitsValue({
          value,
          maximumFractionDigits: 2,
          notation: "compact"
        })
    }));
  };

  const runNumberToRunNameMap = Object.fromEntries(runs.map((run) => [run.number, run.name]));

  const getRunNameByNumber = (number) => runNumberToRunNameMap[number];

  const metaBreakdownConfig = getMetaBreakdownConfig();
  const metricsBreakdownConfig = getMetricsBreakdownConfig();

  const breakdownConfig = [...metaBreakdownConfig, ...metricsBreakdownConfig];

  const implementedMetaBreakdownNames = metaBreakdownConfig
    .filter(({ isNotImplemented }) => !isNotImplemented)
    .map(({ name }) => name);
  const metricsBreakdownNames = metricsBreakdownConfig.map(({ name }) => name);

  const breakdownNames = [...implementedMetaBreakdownNames, ...metricsBreakdownNames];

  const colorsMap = getColorsMap(breakdownNames, theme.palette.chart);

  const { selectedBreakdowns, addBreakdown, removeBreakdown } = useTaskBreakdownState({
    taskId,
    breakdownNames,
    initialSelectedBreakdowns: metricsBreakdownNames,
    fallbackBreakdowns: [METRIC_BREAKDOWN_NAME.DURATION, METRIC_BREAKDOWN_NAME.EXPENSES],
    queryParamName: BREAKDOWN_BY_QUERY_PARAMETER
  });

  return (
    <Layout
      selectedBreakdowns={selectedBreakdowns}
      colorsMap={colorsMap}
      breakdownConfig={breakdownConfig}
      addBreakdown={addBreakdown}
      removeBreakdown={removeBreakdown}
      runs={runs}
      getRunNameByNumber={getRunNameByNumber}
      colors={({ id }) => colorsMap[id]}
    />
  );
};

export default Breakdown;
