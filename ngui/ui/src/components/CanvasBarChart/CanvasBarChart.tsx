import { useRef, useEffect } from "react";
import { Skeleton, Typography } from "@mui/material";
import { useTheme as useMuiTheme } from "@mui/material/styles";
import { lighten } from "@mui/system";
import { ResponsiveBarCanvas } from "@nivo/bar";
import { getInheritedColorGenerator } from "@nivo/colors";
import { ResponsiveWrapper } from "@nivo/core";
import { FormattedMessage } from "react-intl";
import { useMoneyFormatter } from "components/FormattedMoney";
import { useBarChartColors } from "hooks/useChartColors";
import { useChartLayoutOptions } from "hooks/useChartLayoutOptions";
import { useChartTheme } from "hooks/useChartTheme";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { getBarTicks, TICK_COUNT, getMaxAndMinBandValues, getChartWidth, AXIS_FORMATS } from "utils/charts";
import {
  DEFAULT_BAR_CHART_MARGIN,
  DEFAULT_BAR_CHART_HEIGHT,
  DEFAULT_BAR_CHART_PADDING,
  DEFAULT_BAR_CHART_INNER_PADDING,
  DEFAULT_CHART_BORDER_WIDTH,
  FORMATTED_MONEY_TYPES
} from "utils/constants";
import useStyles from "./CanvasBarChart.styles";
import CanvasBarChartPdf from "./CanvasBarChartPdf";
import CanvasBarChartTooltip from "./CanvasBarChartTooltip";

const DEFAULT_LAYERS = ["grid", "axes", "bars", "legends", "annotations", "totals"];

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
  layers = DEFAULT_LAYERS,
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
  minMaxTicksEqualToMinMaxValues,
  enableTotals,
  valueFormat,
  thresholdMarker
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

  const getMaxValue = () => Math.max(...[maxBandValue, thresholdMarker?.value].filter(Boolean));

  const { tickValues, gridValues, maxValue, minValue } = getBarTicks({
    height: wrapperHeight,
    layout,
    ticksCount: TICK_COUNT,
    maxValue: getMaxValue(),
    minValue: minBandValue,
    minMaxTicksEqualToMinMaxValues
  });

  const chartWidth = getChartWidth(wrapperWidth, margin, layout);

  const formatter = useMoneyFormatter();

  const formatAxis = (format) =>
    ({
      [AXIS_FORMATS.MONEY]: (value) => formatter(FORMATTED_MONEY_TYPES.TINY_COMPACT, value, { format: currency }),
      [AXIS_FORMATS.RAW]: (value) => value,
      [AXIS_FORMATS.PERCENTAGE]: (value) => `${value * 100}%`
    })[format];

  const { axisLeft, axisBottom, enableGridX, enableGridY, gridXValues, gridYValues } = useChartLayoutOptions({
    layout,
    formatAxis: formatAxis(axisFormat),
    tickValues,
    chartWidth,
    data,
    indexBy,
    padding,
    chartTheme,
    gridValues,
    enableGridY: enableGridYProperty,
    enableGridX: enableGridXProperty,
    axisBottom: axisBottomProperty,
    axisLeft: axisLeftProperty
  });

  const borderColorProp = { from: "color", modifiers: [["darker", 1.3]] };
  const labelTextColorProp = { from: "color" };

  const getBarSettings = (bar) => {
    const getBarBorderColor = getInheritedColorGenerator(borderColorProp, chartTheme);
    const barBorderColor = getBarBorderColor(bar);

    const getBarLabelColor = getInheritedColorGenerator(labelTextColorProp, chartTheme);
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

  return (
    <div ref={wrapperRef} style={{ height: "100%" }} data-test-id={dataTestId}>
      {pdfId ? <CanvasBarChartPdf pdfId={pdfId} renderData={() => ({ canvasRef })} /> : null}
      <ResponsiveBarCanvas
        data={data}
        keys={keys}
        ref={canvasRef}
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
        borderColor={borderColorProp}
        layout={layout}
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
        layers={[
          ...layers,
          (ctx, layerContext) => {
            if (selectedBar) {
              layerContext.bars.forEach((bar) => {
                drawBar(ctx, getBarSettings(bar));
              });
            }
          },
          (_, { bars }) => {
            barsRef.current = bars.map((bar) => getBarSettings(bar));
          },
          ...(thresholdMarker
            ? [
                (ctx, layerContext) => {
                  const { innerWidth, yScale } = layerContext;

                  const yTotal = yScale(thresholdMarker.value);

                  const x0 = 0;
                  const x1 = innerWidth;
                  const y0 = yTotal;
                  const y1 = yTotal;

                  ctx.strokeStyle = chartTheme.canvas.marker.color;
                  ctx.lineWidth = chartTheme.canvas.marker.lineWidth;

                  ctx.beginPath();
                  ctx.setLineDash(chartTheme.canvas.marker.lineDash);
                  ctx.moveTo(x0, y0);
                  ctx.lineTo(x1, y1);
                  ctx.stroke();

                  const textX0 = innerWidth - chartTheme.canvas.marker.xOffset;
                  const textY0 = yTotal - chartTheme.canvas.marker.yOffset;

                  ctx.textAlign = "right";
                  ctx.fillStyle = chartTheme.canvas.marker.color;
                  const text = thresholdMarker.format?.(thresholdMarker.value) ?? thresholdMarker.value;
                  ctx.font = chartTheme.canvas.marker.font;
                  ctx.fillText(text, textX0, textY0);
                  ctx.restore();
                }
              ]
            : [])
        ]}
        theme={chartTheme}
        axisFormat={AXIS_FORMATS.MONEY}
        labelSkipWidth={labelSkipWidth}
        labelTextColor={labelTextColor}
        enableTotals={enableTotals}
        valueFormat={valueFormat}
      />
    </div>
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
  ...rest
}) => {
  const theme = useMuiTheme();

  const {
    margin = DEFAULT_BAR_CHART_MARGIN,
    height = DEFAULT_BAR_CHART_HEIGHT,
    padding = DEFAULT_BAR_CHART_PADDING,
    innerPadding = DEFAULT_BAR_CHART_INNER_PADDING
  } = style;

  return (
    <div
      style={{
        height: theme.spacing(height)
      }}
    >
      <ResponsiveWrapper>
        {({ width: wrapperWidth, height: wrapperHeight }) => {
          if (isLoading) {
            return <Skeleton variant="rectangular" height={wrapperHeight} />;
          }
          if (isEmptyArray(data) || isEmptyArray(keys)) {
            return (
              <Typography
                component="div"
                style={{
                  height: "100%",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center"
                }}
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
              height={height}
              margin={margin}
              padding={padding}
              innerPadding={innerPadding}
              keys={keys}
              palette={palette || theme.palette.chart}
              {...rest}
            />
          );
        }}
      </ResponsiveWrapper>
    </div>
  );
};

export default ResponsiveCanvasBarChart;
