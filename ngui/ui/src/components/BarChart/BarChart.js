import React, { useRef } from "react";
import Box from "@mui/material/Box";
import { useTheme } from "@mui/material/styles";
import { ResponsiveBar } from "@nivo/bar";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import ChartTooltip from "components/ChartTooltip";
import FormattedMoney from "components/FormattedMoney";
import { useBarChartColors } from "hooks/useChartColors";
import { useChartHoverStyles } from "hooks/useChartHoverStyles";
import { useChartLayoutOptions } from "hooks/useChartLayoutOptions";
import { useChartTheme } from "hooks/useChartTheme";
import { useResizeObserver } from "hooks/useResizeObserver";
import { AXIS_FORMATS, getBarTicks, getChartWidth, getMaxAndMinBandValues, TICK_COUNT } from "utils/charts";
import {
  FORMATTED_MONEY_TYPES,
  DEFAULT_BAR_CHART_HEIGHT,
  DEFAULT_BAR_CHART_MARGIN,
  DEFAULT_CHART_BORDER_WIDTH
} from "utils/constants";
import { isEmpty } from "utils/objects";

const formatAxis = (format) =>
  ({
    [AXIS_FORMATS.MONEY]: (value) => <FormattedMoney value={value} type={FORMATTED_MONEY_TYPES.TINY_COMPACT} />,
    [AXIS_FORMATS.RAW]: (value) => value,
    [AXIS_FORMATS.PERCENTAGE]: (value) => `${value * 100}%`
  }[format]);

const legendSettings = [
  {
    dataFrom: "keys",
    anchor: "bottom-right",
    direction: "column",
    justify: false,
    translateX: 120,
    translateY: 0,
    itemsSpacing: 2,
    itemWidth: 100,
    itemHeight: 20,
    itemDirection: "left-to-right",
    itemOpacity: 0.85,
    symbolSize: 20,
    effects: [
      {
        on: "hover",
        style: {
          itemOpacity: 1
        }
      }
    ]
  }
];

const BarChart = ({
  data,
  keys,
  palette,
  colorsMap = {},
  markers = {},
  showLegend = false,
  style = {},
  indexBy = "id",
  layout = "vertical",
  onClick,
  renderTooltipBody,
  enableLabel = false,
  borderWidth = DEFAULT_CHART_BORDER_WIDTH,
  label,
  dataTestId,
  axisFormat = AXIS_FORMATS.RAW
}) => {
  const intl = useIntl();
  const theme = useTheme();

  const chartPalette = palette || theme.palette.chart;

  const chartTheme = useChartTheme();

  const wrapperRef = useRef(null);
  const { width: wrapperWidth } = useResizeObserver(wrapperRef);

  const { margin = DEFAULT_BAR_CHART_MARGIN } = style;

  const { height = DEFAULT_BAR_CHART_HEIGHT, padding = 0.7, innerPadding = 0 } = style;

  const shouldRenderMarkers = !isEmpty(markers);

  const chartHeight = theme.spacing(height);

  const legend = showLegend ? legendSettings : [];

  const { maxBandValue, minBandValue } = getMaxAndMinBandValues(data, keys);

  const { alwaysDisplay: alwaysDisplayMarkers, value: markersValue } = markers;

  const maxBarValue = shouldRenderMarkers && alwaysDisplayMarkers && markersValue > maxBandValue ? markersValue : maxBandValue;
  const minBarValue = shouldRenderMarkers && alwaysDisplayMarkers && markersValue < minBandValue ? markersValue : minBandValue;

  const { tickValues, gridValues, maxValue, minValue } = getBarTicks({
    height: chartHeight,
    layout,
    ticksCount: TICK_COUNT,
    maxValue: maxBarValue,
    minValue: minBarValue
  });

  /**
   * TODO: Try to use the "useDimensions" hook to get all the dimension parameters as we do for the LineChart
   */
  const chartWidth = getChartWidth(wrapperWidth, margin, layout);

  const { axisLeft, axisBottom, enableGridX, enableGridY, gridXValues, gridYValues } = useChartLayoutOptions({
    layout,
    formatAxis: formatAxis(axisFormat),
    tickValues,
    chartWidth,
    data,
    indexBy,
    padding,
    chartTheme,
    gridValues
  });

  const chartMarkers = shouldRenderMarkers
    ? [
        {
          axis: "y",
          value: markers.value,
          legend: intl.formatNumber(markers.value, { format: markers.format }),
          lineStyle: {
            stroke: theme.palette.error.main,
            strokeDasharray: "10, 10",
            strokeWidth: 2
          },
          textStyle: {
            fill: theme.palette.error.main,
            fontSize: theme.typography.caption.fontSize
          }
        }
      ]
    : [];

  const [wrapperClass, addHoverClass, removeHoverClass] = useChartHoverStyles({ borderWidth });

  const applyHoverStyles = (sectionData, event) => {
    if (onClick) {
      addHoverClass(event.target);
    }
  };

  const removeHoverStyles = (sectionData, event) => {
    if (onClick) {
      removeHoverClass(event.target);
    }
  };

  const colors = useBarChartColors(chartPalette, colorsMap);

  return (
    <Box ref={wrapperRef} className={wrapperClass} height={chartHeight} data-test-id={dataTestId}>
      {chartWidth > 0 && (
        <ResponsiveBar
          data={data}
          keys={keys}
          indexBy={indexBy}
          margin={margin}
          padding={padding}
          innerPadding={innerPadding}
          colors={colors}
          borderWidth={borderWidth}
          borderColor={{ from: "color", modifiers: [["darker", 1.3]] }}
          layout={layout}
          markers={chartMarkers}
          enableGridX={enableGridX}
          enableGridY={enableGridY}
          gridXValues={gridXValues}
          gridYValues={gridYValues}
          maxValue={maxValue}
          minValue={minValue}
          axisLeft={axisLeft}
          axisBottom={axisBottom}
          enableLabel={enableLabel}
          label={label}
          legends={legend}
          animate={false}
          onClick={onClick}
          onMouseEnter={(sectionData, event) => applyHoverStyles(sectionData, event)}
          onMouseLeave={(sectionData, event) => removeHoverStyles(sectionData, event)}
          tooltip={(bandData) => <ChartTooltip body={renderTooltipBody(bandData)} />}
          theme={chartTheme}
        />
      )}
    </Box>
  );
};

BarChart.propTypes = {
  data: PropTypes.array.isRequired,
  keys: PropTypes.array.isRequired,
  fieldTooltipText: PropTypes.array,
  translateTooltip: PropTypes.bool,
  height: PropTypes.number,
  palette: PropTypes.array,
  showLegend: PropTypes.bool,
  colorsMap: PropTypes.object,
  markers: PropTypes.shape({
    value: PropTypes.number.isRequired,
    alwaysDisplay: PropTypes.bool,
    format: PropTypes.string
  }),
  style: PropTypes.object,
  indexBy: PropTypes.string,
  layout: PropTypes.oneOf(["vertical", "horizontal"]),
  onClick: PropTypes.func,
  renderTooltipBody: PropTypes.func.isRequired,
  enableLabel: PropTypes.bool,
  label: PropTypes.func,
  dataTestId: PropTypes.string,
  borderWidth: PropTypes.number,
  axisFormat: PropTypes.oneOf(Object.values(AXIS_FORMATS))
};

export default BarChart;
