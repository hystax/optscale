import { FormattedMessage, FormattedNumber } from "react-intl";
import CompactFormattedNumber from "components/CompactFormattedNumber";
import FormattedDigitalUnit, { IEC_UNITS } from "components/FormattedDigitalUnit";
import { CHART_VALUE_TYPES } from "./constants";
import getColorizedMetricChartLinesAndLegend from "./getColorizedMetricChartLinesAndLegend";

const MAXIMUM_FRACTION_DIGITS = 2;

const getValuesFormatter = (valueType) =>
  ({
    [CHART_VALUE_TYPES.COMPACT_NUMBER]: (value) => <CompactFormattedNumber value={value} />,
    [CHART_VALUE_TYPES.PERCENT]: (value) => (
      <FormattedNumber value={value} format="percentage" maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} />
    ),
    [CHART_VALUE_TYPES.PER_SECOND]: (value) => (
      <FormattedMessage
        id="valuePerSec"
        values={{ value: <FormattedNumber value={value} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} /> }}
      />
    ),
    [CHART_VALUE_TYPES.IEC_BYTE_PER_SECOND]: (value) => (
      <FormattedMessage
        id="valuePerSec"
        values={{
          value: (
            <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.BYTE} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} />
          ),
        }}
      />
    ),
    [CHART_VALUE_TYPES.IEC_BYTE_BASE]: (value) => (
      <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.BYTE} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} />
    ),
    [CHART_VALUE_TYPES.INPUT_OUTPUT_OPERATIONS_PER_SECOND]: (value) => (
      <FormattedMessage
        id="inputOutputOperationsPerSecond"
        values={{ value: <FormattedNumber value={value} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} /> }}
      />
    ),
  })[valueType];

const getMarginLeftByValueType = (valueType) =>
  ({
    [CHART_VALUE_TYPES.COMPACT_NUMBER]: 45,
    [CHART_VALUE_TYPES.PERCENT]: 38,
    [CHART_VALUE_TYPES.PER_SECOND]: 45,
    [CHART_VALUE_TYPES.IEC_BYTE_PER_SECOND]: 69,
    [CHART_VALUE_TYPES.IEC_BYTE_BASE]: 69,
    [CHART_VALUE_TYPES.INPUT_OUTPUT_OPERATIONS_PER_SECOND]: 69,
  })[valueType];

const getChartProps = ({ metricType, valueType, linesWithMarkerData, colors, formatYValue }) => {
  const valuesFormatter = getValuesFormatter(valueType);

  const marginLeft = getMarginLeftByValueType(valueType);

  const { lines, legend } = getColorizedMetricChartLinesAndLegend(
    linesWithMarkerData.map(({ line, markerData }) => ({
      line,
      marker: {
        name: markerData.name,
        title: <FormattedMessage id={markerData.name} />,
        value: valuesFormatter(markerData.value),
        dataTestIds: {
          title: `lbl_${markerData.dataTestIdName}`,
          value: `lbl_${markerData.dataTestIdName}_value`,
        },
      },
    })),
    colors
  );

  return {
    // Formats values in y axis
    formatYAxis: (value) => formatYValue(value),
    marginLeft,
    lines,
    legend,
    // Formats values in a tooltip
    yFormat: (value) => valuesFormatter(value),
    dataTestId: `chart_${metricType}`,
    emptyMessageId: "noDataIsAvailableForThePeriod",
  };
};

export default getChartProps;
