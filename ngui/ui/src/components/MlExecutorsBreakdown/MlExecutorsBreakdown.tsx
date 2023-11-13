import { FormattedNumber, useIntl } from "react-intl";
import FormattedDigitalUnit, { IEC_UNITS, useFormatDigitalUnit } from "components/FormattedDigitalUnit";
import LineChart from "components/LineChart";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { ML_EXECUTORS_DAILY_BREAKDOWN_BY } from "utils/constants";
import { EN_FORMAT_SHORT_YEAR, formatUTC } from "utils/datetime";

const useBreakdownConfig = (breakdownBy) => {
  const intl = useIntl();
  const formatDigitalUnit = useFormatDigitalUnit();

  return {
    [ML_EXECUTORS_DAILY_BREAKDOWN_BY.EXECUTORS_COUNT]: {
      keys: ["executor_count"],
      tooltip: ({ slice }) => slice.points[0].data.yFormatted,
      axisLeft: {
        format: (value) => value
      }
    },
    [ML_EXECUTORS_DAILY_BREAKDOWN_BY.CPU]: {
      keys: ["cpu"],
      tooltip: ({ slice }) => <FormattedNumber format="percentage2" value={slice.points[0].data.y / 100} />,
      axisLeft: {
        format: (value) =>
          intl.formatNumber(value / 100, {
            format: "percentage2"
          })
      }
    },
    [ML_EXECUTORS_DAILY_BREAKDOWN_BY.RAM]: {
      keys: ["ram"],
      tooltip: ({ slice }) => (
        <FormattedDigitalUnit value={slice.points[0].data.y} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />
      ),
      axisLeft: {
        format: (value) =>
          formatDigitalUnit({
            value,
            baseUnit: IEC_UNITS.MEBIBYTE,
            maximumFractionDigits: 2
          })
      }
    },
    [ML_EXECUTORS_DAILY_BREAKDOWN_BY.PROCESS_CPU]: {
      keys: ["process_cpu"],
      tooltip: ({ slice }) => <FormattedNumber format="percentage2" value={slice.points[0].data.y / 100} />,
      axisLeft: {
        format: (value) =>
          intl.formatNumber(value / 100, {
            format: "percentage2"
          })
      }
    },
    [ML_EXECUTORS_DAILY_BREAKDOWN_BY.PROCESS_RAM]: {
      keys: ["process_ram"],
      tooltip: ({ slice }) => (
        <FormattedDigitalUnit value={slice.points[0].data.y} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />
      ),
      axisLeft: {
        format: (value) =>
          formatDigitalUnit({
            value,
            baseUnit: IEC_UNITS.MEBIBYTE,
            maximumFractionDigits: 2
          })
      }
    },
    [ML_EXECUTORS_DAILY_BREAKDOWN_BY.GPU_LOAD]: {
      keys: ["gpu_load"],
      tooltip: ({ slice }) => <FormattedNumber format="percentage2" value={slice.points[0].data.y} />,
      axisLeft: {
        format: (value) =>
          intl.formatNumber(value, {
            format: "percentage2"
          })
      }
    },
    [ML_EXECUTORS_DAILY_BREAKDOWN_BY.GPU_MEMORY_USED]: {
      keys: ["gpu_memory_load"],
      tooltip: ({ slice }) => (
        <FormattedDigitalUnit value={slice.points[0].data.y} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />
      ),
      axisLeft: {
        format: (value) =>
          formatDigitalUnit({
            value,
            baseUnit: IEC_UNITS.MEBIBYTE,
            maximumFractionDigits: 2
          })
      }
    }
  }[breakdownBy];
};

const getBreakdownLine = (breakdown) =>
  Object.entries(breakdown).map(([key, value]) => ({ x: formatUTC(key, EN_FORMAT_SHORT_YEAR), y: value }));

const MlExecutorsBreakdown = ({ breakdownBy, breakdown, isLoading = false }) => {
  const { keys, tooltip, axisLeft } = useBreakdownConfig(breakdownBy);
  const lines = keys.map((key) => ({ id: key, data: getBreakdownLine(breakdown) }));

  return (
    <LineChart
      data={lines.filter(({ data }) => !isEmptyArray(data))}
      renderTooltipBody={tooltip}
      isLoading={isLoading}
      style={{ margin: { top: 25, right: 25, left: 70, bottom: 50 } }}
      axisLeft={axisLeft}
    />
  );
};

export default MlExecutorsBreakdown;
