import { useRef, useEffect } from "react";
import { Box, Skeleton, Typography } from "@mui/material";
import { useTheme as useMuiTheme } from "@mui/material/styles";
import { lighten } from "@mui/system";
import { BarCanvas } from "@nivo/bar";
import { getInheritedColorGenerator } from "@nivo/colors";
import { ResponsiveWrapper } from "@nivo/core";
import { FormattedMessage } from "react-intl";
import { useMoneyFormatter } from "components/FormattedMoney";
import { useBarChartColors } from "hooks/useChartColors";
import { useChartLayoutOptions } from "hooks/useChartLayoutOptions";
import { useChartTheme } from "hooks/useChartTheme";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isEmptyArray } from "utils/arrays";
import { getBarTicks, TICK_COUNT, getMaxAndMinBandValues, getInnerWidth, AXIS_FORMATS, getInnerHeight } from "utils/charts";
import {
  DEFAULT_BAR_CHART_MARGIN,
  DEFAULT_BAR_CHART_HEIGHT,
  DEFAULT_BAR_CHART_PADDING,
  DEFAULT_BAR_CHART_INNER_PADDING,
  DEFAULT_CHART_BORDER_WIDTH,
  FORMATTED_MONEY_TYPES,
  CHART_LEGEND_WIDTH,
  CHART_LEGEND_LAYOUT_SETTINGS
} from "utils/constants";
import useStyles from "./CanvasBarChart.styles";
import CanvasBarChartPdf from "./CanvasBarChartPdf";
import CanvasBarChartTooltip from "./CanvasBarChartTooltip";
import { getChartLayers } from "./layers";

const isBarEmpty = (barData) => barData.value === 0;

const getBarName = (barData) => `${barData.id}.${barData.indexValue}`;

const getRelativeCursorPosition = (event, margin) => {
  const { clientX, clientY } = event;
  const bounds = event.target.getBoundingClientRect();

  return [clientX - bounds.left - margin.left, clientY - bounds.top - margin.top];
};

const isCursorInRect = (rect, cursorPosition) => {
  const { x, y, width, height } = rect;
  const [cursorX, cursorY] = cursorPosition;

  return x <= cursorX && cursorX <= x + width && y <= cursorY && cursorY <= y + height;
};

const drawLabel = (ctx, { label, labelColor, x, y, width, height }) => {
  ctx.textBaseline = "middle";
  ctx.textAlign = "center";
  ctx.fillStyle = labelColor;
  ctx.fillText(label, x + width / 2, y + height / 2);
};

const drawBar = (ctx, settings) => {
  const { bar, borderColor, borderWidth, label, labelColor, shouldRenderLabel } = settings;
  const { color, width, height, x, y } = bar;

  ctx.fillStyle = color;

  ctx.beginPath();

  ctx.rect(x, y, width, height);
  ctx.fill();

  if (borderWidth > 0) {
    ctx.strokeStyle = borderColor;
    ctx.lineWidth = borderWidth;

    ctx.stroke();
  }

  if (shouldRenderLabel) {
    drawLabel(ctx, { label, labelColor, x, y, width, height });
  }
};

const drawHoveredBar = (ctx, settings) => {
  const { bar, borderColor, borderWidth, label, labelColor, shouldRenderLabel } = settings;
  const { color, width, height, x, y } = bar;

  const border = borderWidth === 0 ? 1 : borderWidth;

  ctx.fillStyle = color;

  ctx.beginPath();

  ctx.strokeStyle = borderColor;
  ctx.lineWidth = border;

  ctx.rect(x + border / 2, y + border / 2, width - border, height - border);

  ctx.fill();
  ctx.stroke();

  if (shouldRenderLabel) {
    drawLabel(ctx, { label, labelColor, x, y, width, height });
  }
};

const NULLISH_BAR_KEY = "";

const findBarUnderCursor = (bars, cursorPosition) =>
  bars.find(({ bar }) =>
    isCursorInRect(
      {
        x: bar.x,
        y: bar.y,
        width: bar.width,
        height: bar.height
      },
      cursorPosition
    )
  ) || { bar: { key: NULLISH_BAR_KEY } };

const addClassName = (element, className) => element.classList.add(className);

const removeClassName = (element, className) => element.classList.remove(className);

const useClickableBarHover = ({ refs, margin, isClickable, selectedBar, wrapperDimensions, data }) => {
  const { classes } = useStyles();

  useEffect(() => {
    if (!isClickable) {
      return undefined;
    }

    let previouslyHoveredBarKey = "";
    // Reset saved image data on resize or data change (there is a dependency on wrapperDimensions.width and data)
    let savedImageData = null;

    function mouseMoveHandler(e) {
      e.preventDefault();

      if (!refs.canvasRef.current) {
        return;
      }

      const ctx = refs.canvasRef.current.getContext("2d");
      const bars = refs.barsRef.current;

      // Save current image data *before* drawing a hovered bar
      if (savedImageData === null) {
        savedImageData = ctx.getImageData(0, 0, refs.canvasRef.current.width, refs.canvasRef.current.height);
      }

      const cursorPosition = getRelativeCursorPosition(e, {
        left: margin.left,
        top: margin.top
      });

      const bar = findBarUnderCursor(bars, cursorPosition);

      const currentlyHoveredBarKey = bar.bar.key;

      const previousBarWasJustUnhovered =
        !!previouslyHoveredBarKey &&
        (previouslyHoveredBarKey !== currentlyHoveredBarKey || currentlyHoveredBarKey === NULLISH_BAR_KEY);

      if (previousBarWasJustUnhovered) {
        ctx.putImageData(savedImageData, 0, 0);
      }

      previouslyHoveredBarKey = currentlyHoveredBarKey;

      if (currentlyHoveredBarKey !== NULLISH_BAR_KEY && !isBarEmpty(bar.bar.data)) {
        addClassName(refs.canvasRef.current, classes.hover);
        drawHoveredBar(ctx, bar);
      } else {
        removeClassName(refs.canvasRef.current, classes.hover);
      }
    }

    refs.wrapperRef.current.addEventListener("mousemove", mouseMoveHandler);

    return () => {
      if (refs.wrapperRef.current) {
        refs.wrapperRef.current.removeEventListener("mousemove", mouseMoveHandler);
      }
    };
  }, [
    wrapperDimensions.width,
    refs.wrapperRef,
    refs.canvasRef,
    refs.barsRef,
    margin.left,
    margin.top,
    classes.hover,
    isClickable,
    selectedBar,
    data
  ]);
};

const BORDER_COLOR_PROP = { from: "color", modifiers: [["darker", 1.3]] };
const LABEL_TEXT_COLOR_PROP = { from: "color" };

const CanvasBarChart = ({
  data,
  keys,
  indexBy,
  palette,
  colorsMap = {},
  layout = "vertical",
  enableLabel = false,
  label,
  onClick,
  renderTooltipBody,
  selectedBar,
  borderWidth = DEFAULT_CHART_BORDER_WIDTH,
  pdfId,
  margin,
  padding,
  innerPadding,
  wrapperDimensions,
  axisFormat = AXIS_FORMATS.RAW,
  dataTestId,
  enableGridX: enableGridXProperty,
  enableGridY: enableGridYProperty,
  labelSkipWidth,
  labelTextColor,
  axisBottom: axisBottomProperty,
  axisLeft: axisLeftProperty,
  axisRight: axisRightProperty,
  allocateAdditionalTickAboveMaxValue,
  enableTotals,
  valueFormat,
  thresholdMarker,
  withLegend,
  legendLabel,
  maxValue: maxValueProperty
}) => {
  const wrapperRef = useRef();
  const canvasRef = useRef();
  const barsRef = useRef();

  const { currency } = useOrganizationInfo();

  useClickableBarHover({
    refs: {
      wrapperRef,
      canvasRef,
      barsRef
    },
    margin,
    isClickable: typeof onClick === "function",
    selectedBar,
    wrapperDimensions,
    data
  });

  const chartTheme = useChartTheme();

  const colors = useBarChartColors(palette, colorsMap);

  const { height: wrapperHeight, width: wrapperWidth } = wrapperDimensions;

  const { maxBandValue, minBandValue } = getMaxAndMinBandValues(data, keys);

  const innerWidth = getInnerWidth(wrapperWidth, margin);
  const innerHeight = getInnerHeight(wrapperHeight, margin);

  const getMaxValue = () => Math.max(...[maxBandValue, thresholdMarker?.value, maxValueProperty].filter(Boolean));
  const {
    tickValues: valueTickValues, // ticks on Y axis for vertical layout and X axis for horizontal layout
    gridValues: valueGridValues,
    maxValue,
    minValue
  } = getBarTicks({
    size: layout === "vertical" ? innerWidth : innerHeight,
    ticksCount: TICK_COUNT,
    maxValue: getMaxValue(),
    minValue: minBandValue,
    allocateAdditionalTickAboveMaxValue
  });

  const formatter = useMoneyFormatter();

  const formatValueAxis = (format) =>
    ({
      [AXIS_FORMATS.MONEY]: (value) => formatter(FORMATTED_MONEY_TYPES.TINY_COMPACT, value, { format: currency }),
      [AXIS_FORMATS.RAW]: (value) => value,
      [AXIS_FORMATS.PERCENTAGE]: (value) => `${value * 100}%`
    })[format];

  const { axisLeft, axisRight, axisBottom, enableGridX, enableGridY, gridXValues, gridYValues } = useChartLayoutOptions({
    layout,
    formatValueAxis: typeof axisFormat === "function" ? axisFormat : formatValueAxis(axisFormat),
    valueTickValues,
    valueGridValues,
    innerWidth,
    data,
    indexBy,
    padding,
    chartTheme,
    enableGridY: enableGridYProperty,
    enableGridX: enableGridXProperty,
    axisBottom: axisBottomProperty,
    axisLeft: axisLeftProperty,
    axisRight: axisRightProperty,
    minValue,
    maxValue
  });

  const getBarSettings = (bar) => {
    const getBarBorderColor = getInheritedColorGenerator(BORDER_COLOR_PROP, chartTheme);
    const barBorderColor = getBarBorderColor(bar);

    const getBarLabelColor = getInheritedColorGenerator(LABEL_TEXT_COLOR_PROP, chartTheme);
    const barLabelColor = getBarLabelColor(bar);

    const getSelectionColors = () => (selectedBar === getBarName(bar.data) ? bar.color : lighten(bar.color, 0.8));

    const barColor = selectedBar ? getSelectionColors() : bar.color;

    return {
      bar: {
        ...bar,
        color: barColor
      },
      borderColor: barBorderColor,
      borderWidth,
      labelColor: barLabelColor,
      shouldRenderLabel: enableLabel
    };
  };

  const chartLayers = getChartLayers({
    selectedBar,
    barsRef,
    thresholdMarker,
    withLegend,
    chartTheme,
    drawBar,
    getBarSettings,
    legendLabel
  });

  return (
    <Box
      ref={wrapperRef}
      height={wrapperDimensions.height}
      width={wrapperDimensions.width}
      display="flex"
      data-test-id={dataTestId}
    >
      {pdfId ? <CanvasBarChartPdf pdfId={pdfId} renderData={() => ({ canvasRef })} /> : null}
      <BarCanvas
        data={data}
        keys={keys}
        ref={canvasRef}
        height={wrapperDimensions.height}
        width={wrapperDimensions.width}
        /*
            According to discussions on the github, with `round: true` the chart allocates a bit blank space
            for each band from the left and from the right and if there are a lot of bands than this
            small unused space grows quite large
            Source
              * https://github.com/plouc/nivo/issues/929#issuecomment-1192271248

            See also:
              * https://github.com/plouc/nivo/issues/2019
              * https://github.com/plouc/nivo/issues/840
              * https://github.com/plouc/nivo/issues/929
              * https://github.com/plouc/nivo/pull/1282

            See screenshots with comparisons between round `false` and `true` on large data sets
              * https://gitlab.com/hystax/ngui/-/merge_requests/2902#note_1091122047
        */
        indexScale={{ type: "band", round: false }}
        indexBy={indexBy}
        margin={margin}
        padding={padding}
        innerPadding={innerPadding}
        colors={colors}
        borderWidth={borderWidth}
        borderColor={BORDER_COLOR_PROP}
        layout={layout}
        enableGridX={enableGridX}
        enableGridY={enableGridY}
        gridXValues={gridXValues}
        gridYValues={gridYValues}
        valueScale={{ type: "linear", nice: true, round: false, max: maxValue, min: minValue }}
        axisLeft={axisLeft}
        axisBottom={axisBottom}
        axisRight={axisRight}
        enableLabel={enableLabel}
        label={label}
        animate={false}
        pixelRatio={2}
        onClick={(sectionData) => {
          if (typeof onClick === "function" && !isBarEmpty(sectionData)) {
            onClick(sectionData, getBarName(sectionData));
          }
        }}
        tooltip={(bandData) => {
          if (isBarEmpty(bandData)) {
            return null;
          }

          return <CanvasBarChartTooltip bandData={bandData} renderTooltipBody={renderTooltipBody} barsCount={data.length} />;
        }}
        renderBar={(ctx, settings) => {
          drawBar(ctx, settings);
        }}
        layers={chartLayers}
        theme={chartTheme}
        axisFormat={AXIS_FORMATS.MONEY}
        labelSkipWidth={labelSkipWidth}
        labelTextColor={labelTextColor}
        enableTotals={enableTotals}
        valueFormat={valueFormat}
        legends={
          withLegend
            ? [
                {
                  dataFrom: "keys",
                  ...CHART_LEGEND_LAYOUT_SETTINGS
                }
              ]
            : undefined
        }
      />
    </Box>
  );
};

const ResponsiveCanvasBarChart = ({
  data,
  keys = [],
  style = {},
  isLoading = false,
  emptyMessageId = "noDataToDisplay",
  palette,
  dataTestId,
  withLegend = false,
  ...rest
}) => {
  const muiTheme = useMuiTheme();

  const {
    margin = {
      ...DEFAULT_BAR_CHART_MARGIN,
      right: withLegend ? CHART_LEGEND_WIDTH : DEFAULT_BAR_CHART_MARGIN.right
    },
    height = DEFAULT_BAR_CHART_HEIGHT,
    padding = DEFAULT_BAR_CHART_PADDING,
    innerPadding = DEFAULT_BAR_CHART_INNER_PADDING
  } = style;

  return (
    <div
      style={{
        height: muiTheme.spacing(height)
      }}
    >
      <ResponsiveWrapper>
        {({ width: wrapperWidth, height: wrapperHeight }) => {
          if (isLoading) {
            return <Skeleton variant="rectangular" height={wrapperHeight} width={wrapperWidth} />;
          }
          if (isEmptyArray(data) || isEmptyArray(keys)) {
            return (
              <Typography
                component="div"
                height={wrapperHeight}
                width={wrapperWidth}
                display="flex"
                justifyContent="center"
                alignItems="center"
              >
                <FormattedMessage id={emptyMessageId} />
              </Typography>
            );
          }
          return (
            <CanvasBarChart
              dataTestId={dataTestId}
              wrapperDimensions={{
                width: wrapperWidth,
                height: wrapperHeight
              }}
              data={data}
              margin={margin}
              padding={padding}
              innerPadding={innerPadding}
              keys={keys}
              palette={palette || muiTheme.palette.chart}
              withLegend={withLegend}
              {...rest}
            />
          );
        }}
      </ResponsiveWrapper>
    </div>
  );
};

export default ResponsiveCanvasBarChart;
