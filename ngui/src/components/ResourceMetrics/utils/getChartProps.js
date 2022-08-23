import React from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import FormattedDigitalUnit, { IEC_UNITS } from "components/FormattedDigitalUnit";
import { CHART_VALUE_TYPES } from "./constants";
import getColorizedMetricChartLinesAndLegend from "./getColorizedMetricChartLinesAndLegend";

const MAXIMUM_FRACTION_DIGITS = 2;
const MAXIMUM_Y_AXIS_FRACTION_DIGITS = 1;

const getValuesFormatter = (valueType) =>
  ({
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
          )
        }}
      />
    )
  }[valueType]);

const getYAxisValuesFormatter = (valueType) =>
  ({
    [CHART_VALUE_TYPES.PERCENT]: (value) => (
      <FormattedNumber value={value} format="percentage" maximumFractionDigits={MAXIMUM_Y_AXIS_FRACTION_DIGITS} />
    ),
    [CHART_VALUE_TYPES.PER_SECOND]: (value) => (
      <FormattedMessage
        id="valuePerSec"
        values={{ value: <FormattedNumber value={value} maximumFractionDigits={MAXIMUM_Y_AXIS_FRACTION_DIGITS} /> }}
      />
    ),
    [CHART_VALUE_TYPES.IEC_BYTE_PER_SECOND]: (value) => (
      <FormattedMessage
        id="valuePerSec"
        values={{
          value: (
            <FormattedDigitalUnit
              value={value}
              baseUnit={IEC_UNITS.BYTE}
              maximumFractionDigits={MAXIMUM_Y_AXIS_FRACTION_DIGITS}
            />
          )
        }}
      />
    )
  }[valueType]);

const getMarginLeftByValueType = (valueType) =>
  ({
    [CHART_VALUE_TYPES.PERCENT]: 38,
    [CHART_VALUE_TYPES.PER_SECOND]: 45,
    [CHART_VALUE_TYPES.IEC_BYTE_PER_SECOND]: 69
  }[valueType]);

const getChartProps = ({ metricType, valueType, linesWithMarkerData, colors }) => {
  const valuesFormatter = getValuesFormatter(valueType);
  const yAxisValuesFormatted = getYAxisValuesFormatter(valueType);

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
          value: `lbl_${markerData.dataTestIdName}_value`
        }
      }
    })),
    colors
  );

  return {
    formatYAxis: (value) => yAxisValuesFormatted(value),
    marginLeft,
    lines,
    legend,
    yFormat: (value) => valuesFormatter(value),
    dataTestId: `chart_${metricType}`,
    emptyMessageId: "noDataIsAvailableForThePeriod"
  };
};

export default getChartProps;
